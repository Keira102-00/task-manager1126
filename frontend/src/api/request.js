// axios 实例：请求自动带 token，响应统一拆包，401 跳登录。
import axios from 'axios'
import { message } from 'antd'
import { getToken, removeToken } from '../utils/auth'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// 请求拦截器：有 token 就自动放到 Authorization 头
service.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：后端统一格式 { code, msg, data }
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      return res.data // 直接把 data 交给业务层
    }
    message.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg || '业务错误'))
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.msg || '网络异常，请稍后重试'

    // 401：清掉本地 token 并跳转登录页（已在登录页则不重复跳）
    if (status === 401) {
      removeToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    message.error(msg)
    return Promise.reject(error)
  },
)

export default service
