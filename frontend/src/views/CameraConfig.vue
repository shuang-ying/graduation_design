<template>
  <div class="camera-config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑摄像头' : '添加摄像头' }}</span>
          <el-button @click="handleBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="configRules"
        label-width="100px"
      >
        <el-form-item label="摄像头名称" prop="name">
          <el-input
            v-model="configForm.name"
            placeholder="请输入摄像头名称"
            clearable
          />
        </el-form-item>

        <el-form-item label="RTSP 地址" prop="rtsp_url">
          <el-input
            v-model="configForm.rtsp_url"
            placeholder="请输入 RTSP 流地址，例如：rtsp://admin:password@192.168.1.100:554/stream1"
            clearable
          />
          <div class="form-tip">
            提示：RTSP 地址格式通常为 rtsp://用户名：密码@IP 地址：端口/流名称
          </div>
        </el-form-item>

        <el-form-item label="安装位置" prop="location">
          <el-input
            v-model="configForm.location"
            placeholder="请输入摄像头安装位置（可选）"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            {{ isEdit ? '保存修改' : '添加摄像头' }}
          </el-button>
          <el-button @click="handleTest" :loading="testing">
            测试连接
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { addCamera, updateCamera, getCamera, testCameraConnection } from '@/api/camera'

const router = useRouter()
const route = useRoute()

const configFormRef = ref(null)
const loading = ref(false)
const testing = ref(false)
const isEdit = ref(false)
const cameraId = ref(null)

const configForm = reactive({
  name: '',
  rtsp_url: '',
  location: ''
})

const configRules = {
  name: [
    { required: true, message: '请输入摄像头名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度应在 1-100 个字符之间', trigger: 'blur' }
  ],
  rtsp_url: [
    { required: true, message: '请输入 RTSP 地址', trigger: 'blur' },
    { min: 1, max: 500, message: '地址长度应在 1-500 个字符之间', trigger: 'blur' }
  ]
}

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    cameraId.value = route.params.id
    await loadCameraData()
  }
})

const loadCameraData = async () => {
  try {
    const data = await getCamera(cameraId.value)
    configForm.name = data.name
    configForm.rtsp_url = data.rtsp_url
    configForm.location = data.location || ''
  } catch (error) {
    console.error('加载摄像头数据失败:', error)
  }
}

const handleBack = () => {
  router.push('/cameras')
}

const handleSubmit = async () => {
  if (!configFormRef.value) return
  
  await configFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isEdit.value) {
          await updateCamera(cameraId.value, configForm)
          ElMessage.success('摄像头更新成功')
        } else {
          await addCamera(configForm)
          ElMessage.success('摄像头添加成功')
        }
        router.push('/cameras')
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleTest = async () => {
  if (!configFormRef.value) return
  
  await configFormRef.value.validate(async (valid) => {
    if (valid && configForm.rtsp_url) {
      testing.value = true
      try {
        const tempCameraData = {
          name: configForm.name || 'test',
          rtsp_url: configForm.rtsp_url,
          location: configForm.location
        }
        
        let testId = cameraId.value
        
        if (!testId) {
          const result = await addCamera(tempCameraData)
          testId = result.data.id
          ElMessage.success('临时摄像头创建成功，开始测试连接...')
        }
        
        const result = await testCameraConnection(testId)
        
        if (result.available) {
          ElMessage.success('摄像头连接正常')
        } else {
          ElMessage.warning('摄像头无法连接，请检查 RTSP 地址是否正确')
        }
        
        if (!cameraId.value && testId) {
          await deleteCamera(testId)
        }
      } catch (error) {
        console.error('测试连接失败:', error)
        ElMessage.error('测试连接失败')
      } finally {
        testing.value = false
      }
    } else {
      ElMessage.warning('请先填写 RTSP 地址')
    }
  })
}

import { deleteCamera } from '@/api/camera'
</script>

<style scoped>
.camera-config-container {
  padding: 20px;
}

.config-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
