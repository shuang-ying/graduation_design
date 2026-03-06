// 1. 导入 Vue Router 核心函数：
// createRouter → 创建路由实例；createWebHistory → 用 HTML5 模式（无 # 号）
import { createRouter, createWebHistory } from 'vue-router'
// 2. 导入用户状态（用来判断是否登录）
import { useUserStore } from '@/stores/user'
// 3. 导入页面组件
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Home from '@/views/Home.vue'
import Monitor from '@/views/Monitor.vue'
import CameraList from '@/views/CameraList.vue'
import CameraConfig from '@/views/CameraConfig.vue'
import Playback from '@/views/Playback.vue'

// 4. 定义路由规则：数组里每个对象对应一个“路径-组件”映射
const routes = [
  {
    path: '/',          // 访问 http://localhost:5173/ 时
    redirect: '/home'   // 自动跳转到 /home 路径
  },
  {
    path: '/login',     // 访问 /login 时
    name: 'Login',      // 路由名字（可选，跳转时可以用 name: 'Login'）
    component: Login    // 渲染 Login.vue 组件
  },
  {
    path: '/register',  // 访问 /register 时
    name: 'Register',
    component: Register // 渲染 Register.vue 组件
  },
  {
    path: '/home',      // 访问 /home 时
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }  // 自定义元信息：标记这个页面需要登录才能看
  },
  {
    path: '/monitor',   // 监控页面
    name: 'Monitor',
    component: Monitor,
    meta: { requiresAuth: true }
  },
  {
    path: '/cameras',   // 摄像头列表
    name: 'CameraList',
    component: CameraList,
    meta: { requiresAuth: true }
  },
  {
    path: '/camera-config',   // 添加摄像头
    name: 'CameraConfigAdd',
    component: CameraConfig,
    meta: { requiresAuth: true }
  },
  {
    path: '/camera-config/:id',   // 编辑摄像头
    name: 'CameraConfigEdit',
    component: CameraConfig,
    meta: { requiresAuth: true }
  },
  {
    path: '/playback',  // 录像回放
    name: 'Playback',
    component: Playback,
    meta: { requiresAuth: true }
  }
]

// 5. 创建路由实例：把规则传给路由
const router = createRouter({
  history: createWebHistory(),  // 地址栏没有 # 号（比如 http://localhost:5173/login）
  routes                        // 传入路由规则数组
})

// 6. 路由守卫：页面跳转前的“安检”
router.beforeEach((to, from, next) => {
  // to → 要去的页面；from → 从哪个页面来；next → 放行/跳转的函数
  const userStore = useUserStore()  // 获取用户的 token
  // 判断：要去的页面需要登录（requiresAuth: true），且没有 token → 跳登录页
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')  // 强制跳登录页
  } else {
    next()          // 放行，正常跳转
  }
})

// 7. 导出路由实例（main.js 会导入并挂载）
export default router