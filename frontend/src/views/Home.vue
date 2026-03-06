<!-- src/views/Home.vue -->
<template>
  <div class="home-container">
    <el-card class="home-card">
      <template #header>
        <div class="card-header">
          <span>欢迎 {{ userStore.username }}！</span>
        </div>
      </template>
      <div class="content">
        <p>这是你的毕业设计首页</p>
        <el-button type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()  // 获取用户状态

// 退出登录方法
const handleLogout = async () => {
  try {
    // 弹出确认弹窗：确认是否退出
    await ElMessageBox.confirm(
      '确定要退出登录吗？',  // 提示文字
      '提示',               // 标题
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'     // 警告类型（黄色图标）
      }
    )
    // 用户点“确定”，执行退出
    userStore.logout()  // 清空 Pinia 和 localStorage
    ElMessage.success('已退出登录')
    router.push('/login')  // 跳登录页
  } catch (error) {
    // 用户点“取消”，不做任何操作
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.home-card {
  width: 500px;
  text-align: center;
}

.card-header {
  font-size: 20px;
  font-weight: bold;
}

.content {
  padding: 20px;
}

.content p {
  margin-bottom: 20px;
  font-size: 16px;
}
</style>