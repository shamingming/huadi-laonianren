/**
 * 日期格式化工具
 * @param {Date|string} date - 日期对象或字符串
 * @returns {string} 格式化后的日期 (YYYY-MM-DD HH:mm)
 */
export function formatDate(date) {
  if (!date) return ''

  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).replace(/\//g, '-')
}

// 可选：添加其他日期工具函数
export function formatDateOnly(date) {
  if (!date) return ''
  return new Date(date).toISOString().split('T')[0]
}