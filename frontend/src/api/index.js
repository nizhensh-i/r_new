import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    return Promise.reject(error)
  }
)

// 用户相关接口
export const userApi = {
  // 登录
  login(data) {
    return api.post('/api/login', data)
  },
  // 注册/查询成绩
  register(data) {
    return api.post('/api/cjcx', data)
  },
  // 重置密码
  resetPassword(data) {
    return api.post('/api/reset_password', data)
  },
  // 获取验证码
  getCaptcha() {
    return `http://yzb2.ustc.edu.cn/api/captcha?v=${Math.random()}`
  },
  // 获取个人成绩
  getScore() {
    return api.get('/api/score')
  },
  // 获取公开配置
  getPublicConfig() {
    return api.get('/api/public_config')
  },
  // 登出
  logout() {
    return api.get('/api/logout')
  }
}

// 排名相关接口
export const rankingApi = {
  // 按总分排名
  getRankingByTotal(college, major, page = 1) {
    return api.get(`/api/ranking_total/${encodeURIComponent(college)}/${encodeURIComponent(major)}?page=${page}`)
  },
  // 按除政治后总分排名
  getRankingByNet(college, major, page = 1) {
    return api.get(`/api/ranking_net/${encodeURIComponent(college)}/${encodeURIComponent(major)}?page=${page}`)
  }
}

export default {
  userApi,
  rankingApi
}
