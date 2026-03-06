<template>
  <div class="playback-container">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-card class="video-card">
          <template #header>
            <div class="card-header">
              <span>录像回放</span>
            </div>
          </template>

          <div class="video-wrapper">
            <VideoPlayer
              v-if="currentRecording"
              ref="videoPlayerRef"
              :src="playUrl"
              :is-live="false"
            />
            <div v-else class="no-video">
              <el-empty description="请选择录像文件" />
            </div>
          </div>

          <div class="video-info" v-if="currentRecording">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="录像 ID">{{ currentRecording.id }}</el-descriptions-item>
              <el-descriptions-item label="时长">{{ currentRecording.duration }}秒</el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatTime(currentRecording.start_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ currentRecording.end_time ? formatTime(currentRecording.end_time) : '未完成' }}
              </el-descriptions-item>
              <el-descriptions-item label="文件大小">
                {{ formatFileSize(currentRecording.file_size) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="camera-select-card">
          <template #header>
            <span>选择摄像头</span>
          </template>

          <el-select
            v-model="selectedCameraId"
            placeholder="请选择摄像头"
            style="width: 100%"
            @change="handleCameraChange"
          >
            <el-option
              v-for="camera in cameraList"
              :key="camera.id"
              :label="camera.name"
              :value="camera.id"
            />
          </el-select>
        </el-card>

        <el-card class="recordings-card" style="margin-top: 20px">
          <template #header>
            <span>录像列表</span>
          </template>

          <div v-loading="recordingsLoading" style="min-height: 400px">
            <el-empty v-if="recordings.length === 0" description="暂无录像" />
            
            <div
              v-for="recording in recordings"
              :key="recording.id"
              class="recording-item"
              :class="{ active: currentRecording && currentRecording.id === recording.id }"
              @click="handleSelectRecording(recording)"
            >
              <div class="recording-header">
                <el-icon><VideoPlay /></el-icon>
                <span class="recording-duration">{{ recording.duration }}秒</span>
              </div>
              <div class="recording-time">
                {{ formatTime(recording.start_time) }}
              </div>
              <div class="recording-size">
                {{ formatFileSize(recording.file_size) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import { getCameras } from '@/api/camera'
import { getRecordingsByCamera, getRecordingPlayUrl, deleteRecording, getRecording } from '@/api/recording'
import VideoPlayer from '@/components/VideoPlayer.vue'

const route = useRoute()

const cameraList = ref([])
const recordings = ref([])
const selectedCameraId = ref(null)
const currentRecording = ref(null)
const playUrl = ref('')
const recordingsLoading = ref(false)
const videoPlayerRef = ref(null)

onMounted(async () => {
  await loadCameras()
  
  if (route.query.cameraId) {
    selectedCameraId.value = parseInt(route.query.cameraId)
    await loadRecordings()
  }
})

const loadCameras = async () => {
  try {
    cameraList.value = await getCameras()
  } catch (error) {
    console.error('加载摄像头列表失败:', error)
    ElMessage.error('加载摄像头列表失败')
  }
}

const handleCameraChange = async () => {
  await loadRecordings()
  currentRecording.value = null
  playUrl.value = ''
}

const loadRecordings = async () => {
  if (!selectedCameraId.value) return
  
  recordingsLoading.value = true
  try {
    recordings.value = await getRecordingsByCamera(selectedCameraId.value)
  } catch (error) {
    console.error('加载录像列表失败:', error)
    ElMessage.error('加载录像列表失败')
  } finally {
    recordingsLoading.value = false
  }
}

const handleSelectRecording = async (recording) => {
  try {
    const detail = await getRecording(recording.id)
    currentRecording.value = detail
    playUrl.value = getRecordingPlayUrl(recording.id)
  } catch (error) {
    console.error('加载录像详情失败:', error)
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}
</script>

<style scoped>
.playback-container {
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
  height: 450px;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
}

.no-video {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-info {
  margin-top: 20px;
}

.recording-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.recording-item:hover {
  background-color: #f5f7fa;
  border-color: #409eff;
}

.recording-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
}

.recording-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  color: #409eff;
  font-weight: bold;
}

.recording-duration {
  font-size: 12px;
}

.recording-time {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.recording-size {
  font-size: 12px;
  color: #909399;
}
</style>
