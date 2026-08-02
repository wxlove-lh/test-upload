/**
 * 下载后端导出的Excel文件
 * @param {Blob} blob - 后端返回的blob数据
 * @param {string} [filename] - 文件名，默认按日期生成
 */
export function downloadExport(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || `账目明细_${new Date().toISOString().slice(0, 10)}.xlsx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
