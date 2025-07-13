import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000
})

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