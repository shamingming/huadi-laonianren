import axios from 'axios'
import request from '@/utils/request'

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
// 在老人管理部分添加
export const updateElderly = (id, data) => api.put(`/elderly/${id}`, data)
// 获取指定老人的随访记录
// 在 followUp.js 中添加
export const getFollowUpsByElderly = (elderlyId) => {
  return api.get(`/elderly/${elderlyId}/follow-ups`)// 改用 api 实例，而非 request
}


// 医生管理

// followUp.js
// 医生管理 - 修复参数处理逻辑
export const getDoctors = (params = {}) => {
  // 仅传递有效的参数（避免传递 undefined 的 search 参数）
  const queryParams = {
    skip: params.skip || 0,
    limit: params.limit || 100
  };
  // 只有当 search 有值时才添加 name 参数（后端用 name 过滤）
  if (params.search) {
    queryParams.name = params.search;
  }
  return api.get('/doctors', { params: queryParams });
};export const createDoctor = (data) => api.post('/doctors', data)

export const deleteDoctor = (id) => api.delete(`/doctors/${id}`)
// 在医生管理部分添加
export const updateDoctor = (id, data) => api.put(`/doctors/${id}`, data)
// 随访管理
export const getFollowUps = (params) => {
  return api.get('/follow-ups', {
    params: {
      page: params.page,
      per_page: params.per_page,
      elderly_id: params.elderly_id, // 保留ID查询
      doctor_id: params.doctor_id,   // 保留ID查询
      elderly_name: params.elderly_name,  // 直接传递名字
      doctor_name: params.doctor_name,    // 直接传递名字
      start_date: params.start_date,
      end_date: params.end_date
    }
  })
}


// followUp.js 修改 createFollowUp 方法
export const createFollowUp = (data) => {
  const payload = {
    ...data,
    schedule_strategy: data.schedule_strategy || 'automated',
    is_recurring: data.is_recurring || false
  }

  if (payload.followup_date instanceof Date) {
    payload.followup_date = formatDateToBackend(payload.followup_date)
  }

  return api.post('/follow-ups', payload)
}

export const updateFollowUp = (id, data) => {
  const payload = {
    ...data,
    elderly_id: Number(data.elderly_id),
    doctor_id: Number(data.doctor_id)
  }

  if (payload.followup_date instanceof Date) {
    payload.followup_date = formatDateToBackend(payload.followup_date)
  }

  return api.put(`/follow-ups/${id}`, payload)
}



// 添加日期格式化工具函数
const formatDateToBackend = (date) => {
  const pad = num => num.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

export const deleteFollowUp = (id) => api.delete(`/follow-ups/${id}`)  // 添加此行
// 在随访管理部分添加
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
