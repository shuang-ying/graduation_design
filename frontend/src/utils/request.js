// 1. 导入 axios 库（用来发 ajax 请求）
import axios from 'axios'
// 2. 导入 Pinia 的用户状态（后面会写，用来取 token）
import { useUserStore } from '@/stores/user'
// 3. 导入 Element Plus 的错误提示组件（替代 alert）
import { ElMessage } from 'element-plus'

// 4. 创建 axios 实例：相当于定制一个“专属请求工具”
const request = axios.create({
  baseURL: 'http://localhost:8000/api',  // 所有请求都会自动加这个前缀，比如发 /register 实际是 http://localhost:8000/api/register
  timeout: 5000,                          // 5秒没响应就判定超时，避免一直等
  withCredentials: true                    // 跨域时允许带 Cookie（比如后端的登录态）
})

// 5. 请求拦截器：发请求前的“预处理”
request.interceptors.request.use(
  // 第一个函数：请求能正常发出去时执行
  (config) => {
    const userStore = useUserStore()  // 获取用户的 token、用户名等信息
    // 如果有 token，且请求头存在 → 给请求头加 Authorization（后端验证登录用）
    if (userStore.token && config.headers) {
      config.headers.Authorization = `Bearer ${userStore.token}`  // Bearer 是 JWT 的固定格式
    }
    return config  // 必须返回 config，否则请求发不出去
  },
  // 第二个函数：请求发不出去时（比如网络错）执行
  (error) => {
    return Promise.reject(error)  // 把错误抛出去，让页面处理
  }
)

// 6. 响应拦截器：收到后端回复后的“后处理”
request.interceptors.response.use(
  // 第一个函数：后端正常响应（状态码 200/201 等）时执行
  (response) => {
    return response.data  // 只返回后端的核心数据（比如 {code:200, message:"注册成功"}），省得每次取 response.data
  },
  // 第二个函数：后端响应失败（400/500 等）时执行
  (error) => {
    // 提取错误信息：
    // error.response?.data?.detail → 后端返回的具体错误（比如“用户名已存在”）
    // error.response?.data?.password?.[0] → 密码校验错误（比如“密码过长”）
    // 最后默认“请求失败”
    const message = error.response?.data?.detail || error.response?.data?.password?.[0] || '请求失败'
    ElMessage.error(message)  // 弹出红色提示框，显示错误信息
    return Promise.reject(error)  // 把错误抛出去，让页面的 catch 能抓到
  }
)

// 7. 导出这个定制好的 request 工具，其他文件 import request 就能用
export default request