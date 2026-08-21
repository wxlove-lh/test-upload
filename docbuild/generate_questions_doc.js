/* 会计问题清单文档生成脚本 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
} = require('docx');

const FONT = '微软雅黑';
const PRIMARY = '1F6FB2';
const DARK = '2D3748';
const GRAY = '6B7280';
const LIGHT = 'E8F1FA';

function p(text, opts = {}) {
  const runs = Array.isArray(text) ? text : [{ text, color: opts.color || DARK, bold: opts.bold || false }];
  return new Paragraph({
    children: runs.map(r => new TextRun({
      text: r.text, bold: r.bold, italics: r.italics, color: r.color || opts.color || DARK,
      size: r.size || opts.size || 21, font: r.font || FONT,
    })),
    spacing: { before: opts.before ?? 60, after: opts.after ?? 60, line: opts.line ?? 300 },
    alignment: opts.alignment || AlignmentType.LEFT,
    indent: opts.indent,
    bullet: opts.bullet,
    numbering: opts.numbering,
  });
}
function h1(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: 30, font: FONT, color: PRIMARY })],
    spacing: { before: 360, after: 160 }, heading: HeadingLevel.HEADING_1,
    border: { bottom: { color: PRIMARY, size: 6, style: BorderStyle.SINGLE, space: 4 } },
  });
}
function h2(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: 25, font: FONT, color: DARK })],
    spacing: { before: 240, after: 120 }, heading: HeadingLevel.HEADING_2,
  });
}
function q(num, text) {
  return new Paragraph({
    children: [
      new TextRun({ text: `Q${num}. `, bold: true, color: PRIMARY, font: FONT, size: 21 }),
      new TextRun({ text, font: FONT, size: 21, color: DARK }),
    ],
    spacing: { before: 140, after: 40, line: 300 },
  });
}
function answer() {
  return new Paragraph({
    children: [new TextRun({ text: '回答：', bold: true, color: GRAY, font: FONT, size: 20 }),
      new TextRun({ text: '', font: FONT, size: 20, color: GRAY })],
    spacing: { after: 80, line: 280 },
    border: { bottom: { color: 'DDDDDD', size: 2, style: BorderStyle.SINGLE, space: 2 } },
    indent: { left: 120 },
  });
}

const children = [];

// 封面
children.push(
  new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { before: 1600, after: 0 } }),
  new Paragraph({ children: [new TextRun({ text: '个体户报税产品', bold: true, size: 44, font: FONT, color: PRIMARY })], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
  new Paragraph({ children: [new TextRun({ text: '会计咨询问题清单', bold: true, size: 36, font: FONT, color: DARK })], alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
  new Paragraph({ children: [new TextRun({ text: '—— 请会计帮忙把关，用于产品设计 ——', size: 22, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 600 } }),
  new Paragraph({ children: [new TextRun({ text: '咨询日期：＿＿＿＿＿  咨询人：＿＿＿＿＿', size: 20, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER, spacing: { after: 40 } }),
  new Paragraph({ children: [new TextRun({ text: '会计姓名/联系方式：＿＿＿＿＿＿＿＿＿', size: 20, font: FONT, color: GRAY })], alignment: AlignmentType.CENTER }),
  new Paragraph({ children: [new TextRun({ text: '', font: FONT })], spacing: { after: 0 }, pageBreakBefore: true }),
);

// 使用说明
children.push(h1('使用说明'));
children.push(p('这份清单是给懂个体户报税的会计/代办看的，目的是确认产品设计对不对，避免做出来不合规。可以打印出来，边问边记。'));
children.push(p('全程约 30-40 分钟。如果对方很忙，优先问标注【关键】的问题。', { color: GRAY }));
children.push(p('如果对方回答不了某个问题，不用纠结，继续问下一个，把能回答的拿到就行。', { color: GRAY }));

// 第一部分
children.push(h1('一、客户群体与征收方式（最关键，决定产品做多简单）'));
children.push(p('这一部分的答案，直接决定你的产品要不要做"记账"。先问清楚你的目标客户是怎么被征税的。'));
children.push(q(1, '现在普通的餐饮小店、夫妻店（比如小吃店、早餐店、烧烤店），大多数是核定征收还是查账征收？【关键】'));
children.push(answer());
children.push(q(2, '这两年是不是都在往查账征收转？判断的标准是什么（销售额？注册资金？）？【关键】'));
children.push(answer());
children.push(q(3, '查账征收的店，必须建账吗？如果不建账、不记账，会有什么后果？【关键】'));
children.push(answer());
children.push(q(4, '核定征收和查账征收的店，分别大概占多少比例？'));
children.push(answer());
children.push(q(5, '如果我想做产品服务这类小店，先做哪种征收方式的客户比较容易切入？'));
children.push(answer());

// 第二部分
children.push(h1('二、账本要求（决定"记账功能"做到什么程度）'));
children.push(p('如果你确认客户以查账征收为主，这部分就非常关键。'));
children.push(q(6, '查账征收的个体户，必须做简易账还是复式账？怎么判断？【关键】'));
children.push(answer());
children.push(q(7, '简易账具体需要哪些账（收入账、费用账、购进账、盘点表、利润表）？用"手机流水 + 分类"能不能满足？【关键】'));
children.push(answer());
children.push(q(8, '老板用微信、支付宝收的钱，算收入吗？怎么证明？是否需要单独的经营账户？'));
children.push(answer());
children.push(q(9, '老板平时拍的小票、进货单、转账截图，能不能作为记账凭证？有没有效？【关键】'));
children.push(answer());
children.push(q(10, '如果老板把每天的收支记在手机里（拍凭证+记一笔），到月底/季度末整理成简易账，这个做法税务局认吗？'));
children.push(answer());

// 第三部分
children.push(h1('三、税表与计算（决定产品核心功能怎么做）'));
children.push(p('这是产品"自动生成税表"要依赖的计算规则，问得越细，产品越好做。'));
children.push(q(11, '从一本流水账，到填好 A 表（季度预缴）和 B 表（年度汇算），中间的计算步骤是什么？能不能给我举个具体的例子（收入多少、成本多少、费用多少，最后怎么算出税额）？【关键】'));
children.push(answer());
children.push(q(12, '哪些费用可以抵税（抵扣成本），哪些不能？餐饮店常见的费用（进货、房租、工资、水电、设备）分别怎么处理？【关键】'));
children.push(answer());
children.push(q(13, '年应纳税所得额 ≤200 万减半征收，这个是怎么算的、怎么自动认定的？'));
children.push(answer());
children.push(q(14, '老板有雇工和没有雇工，报税有什么区别？'));
children.push(answer());
children.push(q(15, '如果收入比较乱（有微信、支付宝、现金），怎么确认收入总额最稳妥？'));
children.push(answer());

// 第四部分
children.push(h1('四、凭证存储与导出（产品差异化，你提出的"存截图"想法）'));
children.push(p('你想让老板把所有凭证图片存起来，随时能查、能导出。这部分确认它是否真的有价值、怎么做才合规。'));
children.push(q(16, '个体户的账簿、凭证、票据，按规定要保存几年？（我查到是 10 年，对吗？）【关键】'));
children.push(answer());
children.push(q(17, '如果我把老板的凭证图片都存到系统里，按月份、按类别整理好，能对应到每一笔记账。被查账的时候，能不能直接拿来用？【关键】'));
children.push(answer());
children.push(q(18, '导出的凭证和账本，需要什么格式税务局才认可（打印？PDF？还是必须纸质原件）？'));
children.push(answer());
children.push(q(19, '如果老板丢了一张原始票据，但有系统里存的照片，能不能补救？'));
children.push(answer());

// 第五部分
children.push(h1('五、合规与责任（决定产品怎么免责、怎么不越界）'));
children.push(p('这部分最重要。你要想清楚"做工具帮老板自己报税"和"替老板报税"的边界，避免踩红线。'));
children.push(q(20, '如果我的产品帮老板自动算出税额、生成税表，但由老板自己提交申报——这算"替人报税"吗？需要资质吗？【关键】'));
children.push(answer());
children.push(q(21, '如果老板按产品生成的税表去报，结果算错了被罚款，责任在谁？产品里应该放什么样的免责声明？【关键】'));
children.push(answer());
children.push(q(22, '我卖"工具 + 教程"（教老板自己报税），和卖"代账服务"，在合规上有什么区别？'));
children.push(answer());
children.push(q(23, '产品里如果写上"最终以税务局核定为准，如有疑问请咨询专业会计"，够不够？还需要注意什么？'));
children.push(answer());

// 第六部分
children.push(h1('六、老板最容易出错的地方（决定教程和提醒做哪块）'));
children.push(p('这部分帮你做"报税提醒"和"教学"功能的优先级。'));
children.push(q(24, '你平时接到这类小店老板最多的求助是什么？最容易报错、最容易逾期的环节是哪个？【关键】'));
children.push(answer());
children.push(q(25, '一年下来，个体户最容易漏的是什么？工商年报、汇算清缴、还是季度申报？'));
children.push(answer());
children.push(q(26, '如果一个老板什么都不会，你推荐他用什么方式报税最稳妥？'));
children.push(answer());
children.push(q(27, '如果我做"报税日期提醒"（提前提醒该报税了），除了季度申报和年度汇算，还有哪些日期要提醒？'));
children.push(answer());

// 第七部分
children.push(h1('七、合作可能性（你希望通过会计触达客户）'));
children.push(p('如果你想靠会计帮你推广，这部分可以试探性地问，不用太正式。'));
children.push(q(28, '如果有一个工具能帮老板整理好账本和凭证、生成税表，你作为会计，愿意用吗？或者愿意推荐给你的客户吗？'));
children.push(answer());
children.push(q(29, '你手上大概有多少家这类客户？他们现在是怎么做账报税的？'));
children.push(answer());
children.push(q(30, '如果让你参与设计，你最希望这个工具帮你解决什么？（省时间？数据规范？还是别的）'));
children.push(answer());

// 结尾
children.push(h1('最后'));
children.push(p('非常感谢您抽时间解答！如果方便的话，我还想请您帮我确认一个真实的算例（用一家小店一个季度的真实数据，跑一遍"流水 → 账本 → 税表"），这能帮我把产品做准。'));
children.push(p('再次感谢！', { color: GRAY }));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21, color: DARK } } } },
  sections: [{ children }],
});

const outPath = path.resolve(__dirname, '..', '会计咨询问题清单.docx');
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log('OK → ' + outPath); }).catch(e => { console.error('FAIL', e); process.exit(1); });
