<template>
  <div class="tutorial-page">
    <!-- 顶栏 -->
    <header class="tutorial-top">
      <van-icon name="arrow-left" size="18" class="back-btn" @click="$router.push('/app')" />
      <span class="tutorial-top-title">报税流程教程</span>
      <span class="tutorial-top-right">AI虚拟文员</span>
    </header>

    <div class="tutorial-body">
      <!-- 头图卡 -->
      <div class="hero-card">
        <div class="hero-icon">
          <van-icon name="certificate" size="30" color="#fff" />
        </div>
        <div class="hero-text">
          <h1>报税，跟着这 6 步走</h1>
          <p>平时记好账，申报期照着填，一点都不难。</p>
        </div>
      </div>

      <!-- 六步流程 -->
      <div class="step-card g-card">
        <div class="card-title">报税 6 步流程</div>
        <div v-for="(s, i) in steps" :key="i" class="step-item">
          <div class="step-num">{{ i + 1 }}</div>
          <div class="step-content">
            <div class="step-head">
              <span class="step-title">{{ s.title }}</span>
              <van-icon :name="s.icon" size="16" color="var(--brand)" />
            </div>
            <p class="step-desc">{{ s.desc }}</p>
            <div v-if="s.extra" class="step-extra">{{ s.extra }}</div>
          </div>
        </div>
      </div>

      <!-- 关键时间表 -->
      <div class="timeline-card g-card">
        <div class="card-title">申报时间表（记牢这几个日子）</div>
        <div class="timeline-row">
          <span class="timeline-label">增值税 · 个税预缴</span>
          <span class="timeline-value">季度结束后15日内<br /><small>（1月/4月/7月/10月的15日）</small></span>
        </div>
        <div class="timeline-row">
          <span class="timeline-label">个税年度汇算（B表）</span>
          <span class="timeline-value">次年 3月31日 前</span>
        </div>
        <div class="timeline-row">
          <span class="timeline-label">工商年报</span>
          <span class="timeline-value">每年 1月1日 ~ 6月30日</span>
        </div>
        <div class="timeline-tip">
          提示：不管有没有收入都要申报，逾期按日加收滞纳金（税款×0.05%/日）。
        </div>
        <div class="pending-tag">
          <van-icon name="info-o" size="12" color="var(--warn)" />
          <span>按"期终15日内"通用规则整理；按月还是按季、是否顺延，以税务登记与当月公告为准【待核实】</span>
        </div>
      </div>

      <!-- 老板常问 -->
      <div class="faq-card g-card">
        <div class="card-title">老板常问</div>
        <div v-for="(q, i) in faqs" :key="i" class="faq-item">
          <div class="faq-q">
            <van-icon name="question-o" size="14" color="var(--brand)" />
            <span>{{ q.q }}</span>
          </div>
          <p class="faq-a">{{ q.a }}</p>
        </div>
      </div>

      <!-- 查账征收小贴士 -->
      <div class="tips-card g-card">
        <div class="card-title">查账征收要规范记账</div>
        <p>
          现在税务对个体户查账征收是主流趋势。简易账至少要有：
          <strong>收入账 + 费用账 + 购进账 + 盘点表 + 利润表</strong>。
          用本工具的「AI识别记账」把小票拍下来存好，账自然就规范了。
        </p>
      </div>

      <!-- 免责声明 -->
      <div class="disclaimer-card">
        <div class="disclaimer-title">
          <van-icon name="warning-o" size="14" color="var(--warn)" />
          <span>免责声明</span>
        </div>
        <p>
          本教程为流程指引，不代替专业税务申报；文中税额与额度均为估算参考，
          请以最新税收政策及税务机关核定为准。标有「待核实」的内容尚未最终确认，
          以查证后的最新政策为准。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
const steps = [
  {
    title: '平时记好账',
    icon: 'edit',
    desc: '每笔收入和支出都记进系统；小票拍照上传，自动存成凭证备查。',
    extra: '简易账 = 收入账 + 费用账 + 购进账 + 盘点表',
  },
  {
    title: '申报前，先整理账目',
    icon: 'description',
    desc: '点左侧「报税底稿」一键生成，自动归集收入、成本、费用、利润，还有税负估算。',
  },
  {
    title: '打开电子税务局',
    icon: 'shop-o',
    desc: '电脑搜「你所在省 + 电子税务局」，或手机装「电子税务局」APP，用营业执照信息登录。',
  },
  {
    title: '对照底稿填数',
    icon: 'orders-o',
    desc: '找到「增值税及附加税费申报」和「经营所得个人所得税申报（A表）」，把底稿里的数字对照填进去。',
    extra: '现行政策：季收入30万以内增值税免征（阶段性优惠，以最新公告为准）；没收入也要提交申报（0申报）',
  },
  {
    title: '缴款，留好凭证',
    icon: 'gold-coin-o',
    desc: '有税款就按系统金额缴纳，交完把完税证明截图保存；没税款也要完成申报提交。',
  },
  {
    title: '每年别忘了收尾',
    icon: 'certificate',
    desc: '次年3月31日前完成个税年度汇算（B表）；每年1月1日~6月30日填报工商年报。',
  },
]

const faqs = [
  {
    q: '这个月没做生意，还要报税吗？',
    a: '要。没有收入也要按时申报（0申报），逾期会有滞纳金。',
  },
  {
    q: '免税额度是多少？',
    a: '现行政策：小规模纳税人月销售额10万以内、季销售额30万以内免征增值税。这是阶段性优惠，以最新公告为准【待核实】。',
  },
  {
    q: '小票和账本要保存多久？',
    a: '涉税资料一般要求保存10年备查，建议一直留好，别随手扔【待核实，以当地要求为准】。',
  },
  {
    q: '查账征收是什么意思？',
    a: '税务局按你的账本算税。账记规范了，报税数字就清楚，这是现在的主流趋势。',
  },
]
</script>

<style scoped>
.tutorial-page {
  min-height: 100%;
  background: var(--bg);
  display: flex;
  flex-direction: column;
}

.tutorial-top {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
}

.back-btn {
  cursor: pointer;
  color: var(--ink-2);
}

.tutorial-top-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
}

.tutorial-top-right {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-3);
}

.tutorial-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-width: 820px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 头图卡 */
.hero-card {
  background: linear-gradient(135deg, var(--brand), var(--brand-strong));
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-2);
}

.hero-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hero-text h1 {
  margin: 0 0 6px;
  font-size: 19px;
  color: #fff;
  font-weight: 700;
}

.hero-text p {
  margin: 0;
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
}

/* 通用卡片标题 */
.card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--ink);
  padding-bottom: 10px;
  border-bottom: 2px solid var(--brand);
  margin-bottom: 12px;
}

/* 步骤卡 */
.step-card {
  padding: 18px 20px;
}

.step-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed var(--line);
}

.step-item:last-child {
  border-bottom: none;
  padding-bottom: 2px;
}

.step-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--brand);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
}

.step-desc {
  margin: 0;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.6;
}

.step-extra {
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--brand);
  background: var(--brand-tint);
  border-radius: 6px;
  padding: 6px 10px;
  line-height: 1.5;
}

/* 时间表卡 */
.timeline-card {
  padding: 18px 20px;
}

.timeline-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 0;
  border-bottom: 1px dashed var(--line);
}

.timeline-label {
  font-size: 13px;
  color: var(--ink-2);
}

.timeline-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand);
  text-align: right;
}

.timeline-value small {
  font-size: 10.5px;
  font-weight: 400;
  color: var(--ink-3);
}

.timeline-tip {
  margin-top: 10px;
  font-size: 12px;
  color: var(--warn);
  background: #FFF8EC;
  border-radius: 8px;
  padding: 8px 10px;
  line-height: 1.6;
}

.pending-tag {
  margin-top: 8px;
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 11px;
  color: var(--ink-3);
  line-height: 1.5;
}

/* 常问卡 */
.faq-card {
  padding: 18px 20px;
}

.faq-item {
  padding: 9px 0;
  border-bottom: 1px dashed var(--line);
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-q {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.faq-q .van-icon {
  margin-top: 2px;
}

.faq-a {
  margin: 0;
  font-size: 12.5px;
  color: var(--ink-2);
  line-height: 1.6;
  padding-left: 20px;
}

/* 查账征收贴士 */
.tips-card {
  padding: 18px 20px;
}

.tips-card p {
  margin: 0;
  font-size: 13px;
  color: var(--ink-2);
  line-height: 1.8;
}

.tips-card strong {
  color: var(--brand);
}

/* 免责声明 */
.disclaimer-card {
  background: #FDF8EE;
  border: 1px solid #F0E4C8;
  border-radius: var(--radius-md);
  padding: 14px 16px;
}

.disclaimer-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--warn);
  margin-bottom: 6px;
}

.disclaimer-card p {
  margin: 0;
  font-size: 11.5px;
  color: var(--ink-2);
  line-height: 1.7;
}
</style>
