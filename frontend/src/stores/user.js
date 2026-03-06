// 1. 导入 Pinia 的核心函数：defineStore 用来定义一个“状态仓库”
import { defineStore } from 'pinia'
// 2. 导入 Vue 的 ref：用来定义响应式变量（改值会自动更新页面）
import { ref } from 'vue'

// 3. 定义用户状态仓库：
// 第一个参数 'user' → 仓库唯一名字（不能和其他仓库重名）
// 第二个参数 → 函数，类似 Vue 的 setup()，里面写状态和方法
export const useUserStore = defineStore('user', () => {
  // 4. 定义响应式状态：
  // ref 包裹后，变量变成“响应式”（改值时页面自动刷新）
  // localStorage.getItem('token') → 从浏览器本地存储取 token，刷新页面不丢
  const token = ref(localStorage.getItem('token') || '')  // 没有 token 就为空字符串
  const username = ref(localStorage.getItem('username') || '')

  // 5. 定义修改状态的方法：
  // 页面不能直接改 token.value，要通过方法改（规范）
  const setUserInfo = (data) => {
    token.value = data.token       // ref 变量改值必须加 .value（页面里用不用）
    username.value = data.username
    // 存到 localStorage：浏览器本地存储，关闭浏览器也不会丢
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
  }

  // 6. 退出登录方法：清空所有状态
  const logout = () => {
    token.value = ''          // 清空 token
    username.value = ''       // 清空用户名
    localStorage.clear()      // 清空本地存储（所有数据都删）
  }

  // 7. 返回状态和方法：页面里用 useUserStore() 后，能访问这些变量/方法
  return { token, username, setUserInfo, logout }
})