/**
 * 日期格式化工具
 * @param {Date|string} date - 日期对象或字符串
 * @returns {string} 格式化后的日期 (YYYY-MM-DD HH:mm)
 */

// 如果尚未创建此文件，请创建 src/utils/date.js
export const formatDateToBackend = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const pad = (num) => num.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
}

// 可选：添加其他日期工具函数
export function formatDateOnly(date) {
  if (!date) return ''
  return new Date(date).toISOString().split('T')[0]
}
// utils/date.js
export function formatDate(date) {
  if (!date) return '';

  let formattedDate = '';

  if (date instanceof Date) {
    // 处理 Date 对象
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    formattedDate = `${year}-${month}-${day}`;
  } else if (typeof date === 'string') {
    // 处理字符串
    if (date.length === 8) { // YYYYMMDD 格式
      const year = date.slice(0, 4);
      const month = date.slice(4, 6);
      const day = date.slice(6, 8);
      formattedDate = `${year}-${month}-${day}`;
    } else { // 其他格式，尝试解析
      const parsedDate = new Date(date);
      if (!isNaN(parsedDate.getTime())) {
        const year = parsedDate.getFullYear();
        const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
        const day = String(parsedDate.getDate()).padStart(2, '0');
        formattedDate = `${year}-${month}-${day}`;
      } else {
        // 无法解析，返回原始值
        formattedDate = date;
      }
    }
  } else if (typeof date === 'number') {
    // 处理数字（假设为时间戳）
    const parsedDate = new Date(date);
    if (!isNaN(parsedDate.getTime())) {
      const year = parsedDate.getFullYear();
      const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
      const day = String(parsedDate.getDate()).padStart(2, '0');
      formattedDate = `${year}-${month}-${day}`;
    } else {
      // 无法解析，返回空字符串
      formattedDate = '';
    }
  }

  return formattedDate;
}

