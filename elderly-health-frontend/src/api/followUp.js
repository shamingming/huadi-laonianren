import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 5000
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
export const getFollowUps = (params) => api.get('/follow-ups', { params })
export const createFollowUp = (data) => {
  // 确保日期是字符串格式
  if (data.follow_up_date instanceof Date) {
    data.follow_up_date = formatDateToBackend(data.follow_up_date)
  }
  return api.post('/follow-ups', data)
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
