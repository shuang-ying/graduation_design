// 1. 导入 Vue 核心函数：createApp 是 Vue3 创建应用的入口
import { createApp } from 'vue'
// 2. 导入 Pinia 核心函数：createPinia 用来创建状态管理实例
import { createPinia } from 'pinia'
// 3. 导入 Element Plus 核心库（所有 UI 组件都在这）
import ElementPlus from 'element-plus'
// 4. 导入 Element Plus 的样式文件（必须加，否则组件没有样式）
import 'element-plus/dist/index.css'
// 5. 导入 Element Plus 所有图标（* as 表示把图标打包成一个对象）
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 6. 导入根组件（App.vue 是项目的最外层组件）
import App from './App.vue'
// 7. 导入路由配置（后面会写 router/index.js）
import router from './router'

// 8. 创建 Vue 应用实例，传入根组件 App
const app = createApp(App)

// 9. 循环注册所有 Element Plus 图标（比如 <User />、<Lock /> 图标）
// Object.entries 把图标对象转成 [图标名, 图标组件] 的数组
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)  // 注册为全局组件，所有页面都能直接用
}

// 10. 挂载插件（Vue3 必须用 app.use() 挂载插件）
app.use(createPinia())  // 让整个项目能用 Pinia 存数据
app.use(router)         // 让整个项目能用路由跳转页面
app.use(ElementPlus)    // 让整个项目能用 Element Plus 的组件（比如 el-button、el-form）

// 11. 挂载应用：把 Vue 渲染到 index.html 里的 <div id="app"></div>
app.mount('#app')