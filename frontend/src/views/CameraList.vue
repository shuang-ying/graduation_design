<template>
  <div class="camera-list-container">
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>摄像头管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加摄像头
          </el-button>
        </div>
      </template>

      <el-table
        :data="cameraList"
        v-loading="loading"
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="location" label="位置" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'">
              {{ row.status ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="录像中" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_recording ? 'warning' : 'info'">
              {{ row.is_recording ? '录像中' : '未录像' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleMonitor(row)"
            >
              监控
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handlePlayback(row)"
            >
              回放
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getCameras, deleteCamera } from '@/api/camera'

const router = useRouter()

const cameraList = ref([])
const loading = ref(false)

onMounted(() => {
  loadCameras()
})

const loadCameras = async () => {
  loading.value = true
  try {
    cameraList.value = await getCameras()
  } catch (error) {
    console.error('加载摄像头列表失败:', error)
    ElMessage.error('加载摄像头列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  router.push('/camera-config')
}

const handleMonitor = (row) => {
  router.push(`/monitor?cameraId=${row.id}`)
}

const handlePlayback = (row) => {
  router.push(`/playback?cameraId=${row.id}`)
}

const handleEdit = (row) => {
  router.push(`/camera-config/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除摄像头"${row.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteCamera(row.id)
    ElMessage.success('删除成功')
    loadCameras()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}
</script>

<style scoped>
.camera-list-container {
  padding: 20px;
}

.list-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}
</style>
