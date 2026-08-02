import logging
import concurrent.futures
from services.deepseek_service import DeepSeekService

logger = logging.getLogger(__name__)

# 金额差异阈值：≤2% 视为匹配
AMOUNT_DIFF_THRESHOLD = 0.02


class ComparisonService:
    """双次识别比对服务：并行调用两次AI，比对结果并给出置信度"""

    def __init__(self):
        self.deepseek = DeepSeekService()

    def dual_recognize(self, image_bytes: bytes) -> dict:
        """
        双次识别并比对。
        用两个不同温度（0.3和0.7）并行调用DeepSeek，然后比对结果。

        Args:
            image_bytes: 图片二进制数据

        Returns:
            合并后的识别结果字典，包含confidence和match_status
        """
        # 并行调两次（温度0.3和0.7）
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(self.deepseek.recognize_with_temperature, image_bytes, 0.3)
            future_b = executor.submit(self.deepseek.recognize_with_temperature, image_bytes, 0.7)

            try:
                result_a = future_a.result(timeout=60)
            except concurrent.futures.TimeoutError:
                logger.error("第一次识别（temp=0.3）超时")
                raise RuntimeError("AI识别超时（第一次），请稍后重试")
            except Exception as e:
                logger.error("第一次识别（temp=0.3）失败: %s", str(e))
                raise

            try:
                result_b = future_b.result(timeout=60)
            except concurrent.futures.TimeoutError:
                logger.error("第二次识别（temp=0.7）超时")
                raise RuntimeError("AI识别超时（第二次），请稍后重试")
            except Exception as e:
                logger.error("第二次识别（temp=0.7）失败: %s", str(e))
                raise

        logger.info("第一次识别结果: %s", result_a)
        logger.info("第二次识别结果: %s", result_b)

        # 比对逻辑
        return self._compare(result_a, result_b)

    def _compare(self, result_a: dict, result_b: dict) -> dict:
        """比对两次识别结果，返回合并结果与置信度

        Args:
            result_a: 第一次识别结果（温度0.3，更确定性）
            result_b: 第二次识别结果（温度0.7，更多样性）

        Returns:
            合并后的结果字典
        """
        merged = {}
        confidence = {}
        all_matched = True

        # ---- 金额比对：差距≤2%算匹配 ----
        amount_a = self._safe_float(result_a.get('amount', 0))
        amount_b = self._safe_float(result_b.get('amount', 0))
        max_amount = max(amount_a, amount_b, 0.01)
        amount_diff = abs(amount_a - amount_b) / max_amount

        if amount_diff <= AMOUNT_DIFF_THRESHOLD:
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'high'
        elif amount_diff <= 0.05:
            # 差距在2%~5%之间，中等置信度
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'medium'
            all_matched = False
        else:
            merged['amount'] = round(amount_a, 2)
            confidence['amount'] = 'low'
            all_matched = False

        # ---- 分类比对：完全一致算匹配 ----
        cat_a = str(result_a.get('category', '')).strip()
        cat_b = str(result_b.get('category', '')).strip()
        if cat_a and cat_a == cat_b:
            merged['category'] = cat_a
            confidence['category'] = 'high'
        elif cat_a:
            merged['category'] = cat_a
            confidence['category'] = 'low'
            all_matched = False
        else:
            merged['category'] = cat_b or ''
            confidence['category'] = 'low'
            all_matched = False

        # ---- 供应商比对：完全一致算匹配 ----
        sup_a = str(result_a.get('supplier', '')).strip()
        sup_b = str(result_b.get('supplier', '')).strip()
        if sup_a and sup_a == sup_b:
            merged['supplier'] = sup_a
            confidence['supplier'] = 'high'
        elif sup_a:
            merged['supplier'] = sup_a
            confidence['supplier'] = 'low'
            all_matched = False
        else:
            merged['supplier'] = sup_b or ''
            confidence['supplier'] = 'low'
            all_matched = False

        # ---- 日期：优先用第一次的结果 ----
        date_a = str(result_a.get('transaction_date', '')).strip()
        date_b = str(result_b.get('transaction_date', '')).strip()
        merged['transaction_date'] = date_a or date_b
        if date_a and date_a == date_b:
            confidence['date'] = 'high'
        elif date_a:
            confidence['date'] = result_a.get('confidence_date', 'medium')
        else:
            confidence['date'] = 'low'
            all_matched = False

        # ---- 类型：优先用第一次的结果 ----
        merged['type'] = str(result_a.get('type', '支出')).strip()

        # ---- 备注 ----
        merged['notes'] = str(result_a.get('notes', '') or '').strip()

        # ---- 汇总 ----
        merged['confidence'] = confidence
        merged['match_status'] = 'matched' if all_matched else 'needs_check'

        return merged

    @staticmethod
    def _safe_float(value) -> float:
        """安全地将值转换为浮点数"""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
