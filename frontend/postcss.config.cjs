// 说明：曾使用 postcss-px-to-viewport-8-plugin 做"手机端等比缩放"，
// 它把 1px 按 375 宽手机屏幕换算成 vw，导致在电脑浏览器上被放大数倍。
// 现已关闭，页面在电脑上按正常像素显示；手机端由各页面自身的响应式布局处理。
module.exports = {
  plugins: {},
}
