import os
import json
import base64
import re
import logging
from openai import OpenAI
from PIL import Image
import io

logger = logging.getLogger(__name__)


class DeepSeekService:
    """DeepSeek视觉模型调用服务，用于识别收据图片"""

    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.prompt = self._load_prompt()

    def _load_prompt(self):
        """加载提示词文件"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'prompts', 'receipt_prompt.txt'
        )
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("提示词文件未找到: %s，使用默认提示词", prompt_path)
            return "你是一个专门帮饭店记账的AI文员，请从图片中提取交易信息并以纯JSON格式返回。"

    def compress_image(self, image_bytes: bytes, max_size_mb: float = 2.0) -> bytes:
        """压缩图片到指定大小以内（MB）

        Args:
            image_bytes: 原始图片二进制数据
            max_size_mb: 目标最大文件大小（MB）

        Returns:
            压缩后的JPEG二进制数据
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 先缩小尺寸（如果图片非常大）
            max_dim = 1920
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 逐步降低JPEG质量
            quality = 85
            buffer = io.BytesIO()
            while True:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality)
                size_mb = buffer.tell() / (1024 * 1024)
                if size_mb <= max_size_mb or quality <= 20:
                    break
                quality -= 15

            return buffer.getvalue()

        except Exception as e:
            logger.error("图片压缩失败: %s", str(e))
            # 压缩失败则返回原图，让API端处理
            return image_bytes

    def recognize(self, image_bytes: bytes, temperature: float = 0.3) -> dict:
        """
        调用DeepSeek识别图片中的收据信息

        Args:
            image_bytes: 图片二进制数据
            temperature: 生成温度，较低更确定性

        Returns:
            解析后的收据信息字典
        """
        # 压缩图片
        compressed = self.compress_image(image_bytes)
        # 转base64
        b64_image = base64.b64encode(compressed).decode('utf-8')

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]}
                ],
                temperature=temperature,
                max_tokens=2000,
                timeout=30,
            )

            content = response.choices[0].message.content
            logger.info("DeepSeek原始返回 (temp=%.1f): %s", temperature, content)
            return self._parse_response(content)

        except Exception as e:
            logger.error("DeepSeek API调用失败 (temp=%.1f): %s", temperature, str(e))
            raise RuntimeError(f"AI识别服务调用失败: {str(e)}")

    def recognize_with_temperature(self, image_bytes: bytes, temperature: float) -> dict:
        """指定温度调用识别（供双次比对使用）

        Args:
            image_bytes: 图片二进制数据
            temperature: 生成温度

        Returns:
            解析后的收据信息字典
        """
        return self.recognize(image_bytes, temperature=temperature)

    def _parse_response(self, content: str) -> dict:
        """解析AI返回的内容为JSON字典

        支持多种格式：
        - 纯JSON字符串
        - ```json ... ``` 代码块包裹
        - 带有前后多余文字的内容（正则提取）

        Args:
            content: AI返回的原始文本

        Returns:
            解析后的字典
        """
        if not content or not content.strip():
            raise ValueError("AI返回内容为空")

        text = content.strip()

        # 1. 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 去除markdown代码块包裹
        md_pattern = r'^```(?:json)?\s*\n?(.*?)\n?\s*```$'
        md_match = re.search(md_pattern, text, re.DOTALL)
        if md_match:
            try:
                return json.loads(md_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. 用正则找到第一个完整的JSON对象（花括号配对）
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 4. 更宽松的匹配：找所有 {...} 块
        for match in re.finditer(r'\{.*?\}', text, re.DOTALL):
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue

        # 5. 所有方式都失败
        logger.error("无法解析AI返回内容: %s", text[:500])
        raise ValueError(f"无法解析AI返回的JSON内容: {text[:200]}")
