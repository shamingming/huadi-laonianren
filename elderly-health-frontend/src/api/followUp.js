import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 5000
})

// 添加响应拦截器，统一处理数据格式
api.interceptors.response.use(response => {
  // 添加调试日志：打印所有API响应
  console.log('[DEBUG] API响应拦截:', response.config.url, response.data)
  return response
}, error => {
  console.error('[ERROR] API请求失败:', error)
  return Promise.reject(error)
})

// 老人管理
export const getElderlies = (params) => api.get('/elderly', { params })
export const createElderly = (data) => api.post('/elderly', data)
export const deleteElderly = (id) => api.delete(`/elderly/${id}`)

// 医生管理
export const getDoctors = (params) => api.get('/doctors', { params })
export const createDoctor = (data) => api.post('/doctors', data)
export const deleteDoctor = (id) => api.delete(`/doctors/${id}`)

// 随访管理
export const getFollowUps = (params = {}) => {
  // 过滤掉undefined/null的参数
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v !== undefined && v !== null)
  )
  return api.get('/follow-ups', { params: filteredParams })
}
// followUp.js 修改 createFollowUp 方法
export const createFollowUp = (data) => {
  // 确保包含所有必填字段
  const payload = {
    ...data,
    schedule_strategy: data.schedule_strategy || 'manual',
    schedule_interval: data.schedule_interval || 30,
    is_recurring: data.is_recurring || false
  }

  if (payload.follow_up_date instanceof Date) {
    payload.follow_up_date = formatDateToBackend(payload.follow_up_date)
  }

  return api.post('/follow-ups', payload)
}


// 添加日期格式化工具函数
const formatDateToBackend = (date) => {
  const pad = num => num.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

export const deleteFollowUp = (id) => api.delete(`/follow-ups/${id}`)  // 添加此行
export const generateReport = (id) => {
  return api.get(`/follow-ups/${id}/report`, {
    responseType: 'blob',
    headers: {
      'Accept': 'text/html'
    }
  })
}
export const getFollowUpReport = (id) => api.get(`/follow-ups/${id}/report`)
export default {
  // 获取随访列表
  async getFollowUps(params = {}) {
    const res = await api.get('/follow-ups', { params })
    return res.data
  },

  // 创建随访记录
  async createFollowUp(data) {
    const res = await api.post('/api/v1/follow-ups', data)
    return res.data
  },

  // 获取报告（HTML格式）
  async getReport(id) {
    const res = await api.get(`/follow-ups/${id}/report`, {
      responseType: 'blob'
    })
    return res.data
  }
}
