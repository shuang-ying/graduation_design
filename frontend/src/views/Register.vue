<!-- src/views/Register.vue -->
<template>
  <!-- 页面容器：让表单居中 -->
  <div class="register-container">
    <!-- Element Plus 卡片组件：带阴影，美观 -->
    <el-card class="register-card" shadow="hover">
      <!-- 卡片头部：自定义标题 -->
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>

      <!-- Element Plus 表单组件：带验证 -->
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <!-- 用户名输入项 -->
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <!-- 邮箱输入项（可选） -->
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱（可选）"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <!-- 密码输入项 -->
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（6-72位）"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <!-- 确认密码输入项 -->
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <!-- 按钮组 -->
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleRegister" :loading="loading">
            注册
          </el-button>
          <div style="text-align: center; margin-top: 10px">
            <span>已有账号？</span>
            <router-link to="/login" style="color: #409eff">去登录</router-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// 1. 获取路由实例（用来跳转页面）
const router = useRouter()

// 2. 表单 ref：用来调用验证方法
const registerFormRef = ref(null)
// 3. 加载状态：按钮转圈，防止重复点击
const loading = ref(false)

// 4. 表单数据：用 reactive 定义复杂对象（响应式）
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 5. 表单验证规则：Element Plus 自带验证
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },  // 失去焦点验证
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }  // 验证邮箱格式
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 72, message: '密码长度在 6 到 72 个字符', trigger: 'blur' }  // 限制密码长度
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    // 自定义验证：两次密码一致
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()  // 验证通过
        }
      },
      trigger: 'blur'
    }
  ]
}

// 6. 注册提交方法
const handleRegister = async () => {
  // 先判断表单 ref 是否存在
  if (!registerFormRef.value) return
  // 调用表单验证：所有规则通过才执行后续逻辑
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true  // 按钮转圈，防止重复提交
      try {
        // 发注册请求（用封装的 request）
        const res = await request.post('/register', {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          confirm_password: registerForm.confirmPassword  // 后端字段是下划线，前端是驼峰，要转换
        })
        // 注册成功
        if (res.code === 200) {
          ElMessage.success('注册成功，请登录')  // 成功提示
          router.push('/login')  // 跳登录页
        }
      } catch (error) {
        // 注册失败（比如用户名已存在），控制台打印错误
        console.error('注册失败：', error)
      } finally {
        loading.value = false  // 不管成功失败，都停止转圈
      }
    }
  })
}
</script>

<style scoped>
/* 页面容器：全屏 + flex 居中 */
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

/* 卡片宽度 */
.register-card {
  width: 450px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}
</style>