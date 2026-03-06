<template>
  <div class="monitor-container">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-card class="video-card">
          <template #header>
            <div class="card-header">
              <span>{{ currentCamera ? currentCamera.name : '实时监控' }}</span>
              <el-select
                v-model="selectedCameraId"
                placeholder="选择摄像头"
                style="width: 200px"
                @change="handleCameraChange"
              >
                <el-option
                  v-for="camera in cameraList"
                  :key="camera.id"
                  :label="camera.name"
                  :value="camera.id"
                />
              </el-select>
            </div>
          </template>

          <div class="video-wrapper">
            <VideoPlayer
              v-if="streamUrl"
              ref="videoPlayerRef"
              :src="streamUrl"
              :is-live="true"
            />
            <div v-else class="no-camera">
              <el-empty description="请选择摄像头" />
            </div>
          </div>

          <div class="control-bar">
            <el-button
              type="danger"
              :loading="recording"
              @click="handleRecording"
              :disabled="!selectedCameraId"
            >
              <el-icon><VideoCamera /></el-icon>
              {{ recording ? '停止录像' : '开始录像' }}
            </el-button>
            
            <el-input-number
              v-model="recordingDuration"
              :min="1"
              :max="600"
              :step="10"
              style="margin-left: 20px"
              :disabled="recording"
            />
            <span style="margin-left: 10px">秒</span>

            <el-tag
              v-if="recording"
              type="danger"
              effect="dark"
              style="margin-left: 20px"
            >
              录像中...
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="camera-list-card">
          <template #header>
            <span>摄像头列表</span>
          </template>

          <el-table
            :data="cameraList"
            v-loading="loading"
            style="width: 100%"
            size="small"
            @row-click="handleRowClick"
          >
            <el-table-column prop="name" label="名称" />
            <el-table-column label="状态" width="60">
              <template #default="{ row }">
                <el-tag :type="row.status ? 'success' : 'danger'" size="small">
                  {{ row.status ? '在线' : '离线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="录像" width="60">
              <template #default="{ row }">
                <el-tag :type="row.is_recording ? 'warning' : 'info'" size="small">
                  {{ row.is_recording ? '录制' : '空闲' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="info-card" style="margin-top: 20px">
          <template #header>
            <span>摄像头信息</span>
          </template>

          <div v-if="currentCamera" class="info-content">
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="名称">{{ currentCamera.name }}</el-descriptions-item>
              <el-descriptions-item label="位置">{{ currentCamera.location || '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="currentCamera.status ? 'success' : 'danger'" size="small">
                  {{ currentCamera.status ? '在线' : '离线' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="RTSP 地址">
                <el-tooltip :content="currentCamera.rtsp_url" placement="top">
                  <span style="font-size: 12px">{{ currentCamera.rtsp_url.substring(0, 30) }}...</span>
                </el-tooltip>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="请选择摄像头" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'
import { getCameras, getStreamUrl } from '@/api/camera'
import { startRecording, stopRecording } from '@/api/recording'
import { useMonitorStore } from '@/stores/monitor'
import VideoPlayer from '@/components/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()
const monitorStore = useMonitorStore()

const cameraList = ref([])
const loading = ref(false)
const selectedCameraId = ref(null)
const streamUrl = ref('')
const recording = ref(false)
const recordingDuration = ref(60)
const videoPlayerRef = ref(null)
const refreshTimer = ref(null)

const currentCamera = computed(() => {
  return cameraList.value.find(c => c.id === selectedCameraId.value) || null
})

onMounted(() => {
  loadCameras()
  
  if (route.query.cameraId) {
    selectedCameraId.value = parseInt(route.query.cameraId)
    updateStreamUrl()
  }
  
  startRefreshTimer()
})

onBeforeUnmount(() => {
  stopRefreshTimer()
})

const loadCameras = async () => {
  loading.value = true
  try {
    cameraList.value = await getCameras()
    
    if (selectedCameraId.value) {
      const camera = cameraList.value.find(c => c.id === selectedCameraId.value)
      if (camera) {
        updateCameraStatus(camera)
      }
    }
  } catch (error) {
    console.error('加载摄像头列表失败:', error)
    ElMessage.error('加载摄像头列表失败')
  } finally {
    loading.value = false
  }
}

const handleCameraChange = () => {
  updateStreamUrl()
  monitorStore.setCurrentCamera(currentCamera.value)
}

const handleRowClick = (row) => {
  selectedCameraId.value = row.id
  handleCameraChange()
}

const updateStreamUrl = () => {
  if (selectedCameraId.value) {
    streamUrl.value = getStreamUrl(selectedCameraId.value)
  } else {
    streamUrl.value = ''
  }
}

const handleRecording = async () => {
  if (!selectedCameraId.value) {
    ElMessage.warning('请先选择摄像头')
    return
  }

  if (recording.value) {
    await stopRecordingAction()
  } else {
    await startRecordingAction()
  }
}

const startRecordingAction = async () => {
  try {
    await startRecording(selectedCameraId.value, recordingDuration.value)
    recording.value = true
    monitorStore.addRecordingCamera(selectedCameraId.value)
    ElMessage.success(`开始录像，预计录制${recordingDuration.value}秒`)
    
    // 立即刷新摄像头列表，更新录像状态
    await loadCameras()
    
    // 录像结束后自动刷新
    setTimeout(async () => {
      recording.value = false
      monitorStore.removeRecordingCamera(selectedCameraId.value)
      await loadCameras()  // 刷新状态
      ElMessage.success('录像已完成')
    }, recordingDuration.value * 1000 + 2000)
  } catch (error) {
    console.error('开始录像失败:', error)
    recording.value = false
  }
}

const stopRecordingAction = async () => {
  try {
    await stopRecording(selectedCameraId.value)
    recording.value = false
    monitorStore.removeRecordingCamera(selectedCameraId.value)
    ElMessage.success('录像已停止')
    await loadCameras()  // 立即刷新状态
  } catch (error) {
    console.error('停止录像失败:', error)
  }
}

const updateCameraStatus = (camera) => {
  const index = cameraList.value.findIndex(c => c.id === camera.id)
  if (index > -1) {
    cameraList.value[index] = camera
  }
}

const startRefreshTimer = () => {
  refreshTimer.value = setInterval(() => {
    loadCameras()
  }, 5000)
}

const stopRefreshTimer = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}
</script>

<style scoped>
.monitor-container {
  padding: 20px;
}

.video-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.video-wrapper {
  height: 500px;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
}

.no-camera {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-bar {
  margin-top: 20px;
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.camera-list-card,
.info-card {
  height: fit-content;
}

.info-content {
  font-size: 14px;
}
</style>
