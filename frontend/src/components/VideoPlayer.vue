<template>
  <div class="video-player-container">
    <!-- 直播模式 -->
    <div v-if="isLive && src" class="video-wrapper">
      <img 
        ref="videoImg"
        :src="streamSrc"
        class="mjpeg-stream"
        alt="视频流"
      />
      <div class="video-overlay">
        <span class="live-badge">直播中</span>
      </div>
    </div>
    
    <!-- 录像回放模式（下载模式） -->
    <div v-else-if="src && !isLive" class="video-wrapper download-mode">
      <div class="download-content">
        <el-icon :size="60" color="#409eff"><VideoPlay /></el-icon>
        <p class="video-title">录像文件</p>
        <div class="download-actions">
          <el-button type="primary" @click="downloadVideo">
            <el-icon><Download /></el-icon>
            下载录像
          </el-button>
          <el-button @click="openInNewTab">
            <el-icon><VideoCamera /></el-icon>
            在新窗口播放
          </el-button>
        </div>
        <p class="video-hint">提示：点击下载录像文件，或在新窗口播放</p>
      </div>
    </div>
    
    <!-- 无信号 -->
    <div v-else class="no-signal">
      <el-empty description="请选择摄像头" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { VideoPlay, Download, VideoCamera } from '@element-plus/icons-vue'

const props = defineProps({
  src: {
    type: String,
    default: ''
  },
  isLive: {
    type: Boolean,
    default: false
  }
})

const videoImg = ref(null)

// 直播流地址转换
const streamSrc = computed(() => {
  if (!props.src) return ''
  
  // 如果是 /api/stream/xxx 格式，转换为 /api/video/xxx
  const match = props.src.match(/\/api\/stream\/(\d+)/)
  if (match) {
    return `http://localhost:8000/api/video/${match[1]}`
  }
  
  return props.src
})

// 下载录像文件
const downloadVideo = () => {
  if (!props.src) return
  
  const link = document.createElement('a')
  link.href = props.src
  link.download = `recording_${Date.now()}.mp4`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 在新窗口打开播放
const openInNewTab = () => {
  if (!props.src) return
  window.open(props.src, '_blank')
}

// 监听视频源变化
watch(() => props.src, (newSrc) => {
  console.log('视频源变化:', newSrc)
}, { immediate: true })
</script>

<style scoped>
.video-player-container {
  width: 100%;
  height: 100%;
  background-color: #000;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.video-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.mjpeg-stream {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.download-mode {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #000;
}

.download-content {
  text-align: center;
  color: #fff;
  padding: 40px;
}

.video-title {
  font-size: 18px;
  margin: 20px 0;
  color: #e0e0e0;
}

.download-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 20px 0;
}

.video-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 15px;
}

.video-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
}

.live-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: rgba(220, 53, 69, 0.9);
  color: white;
  font-size: 12px;
  font-weight: bold;
  border-radius: 4px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.no-signal {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #000;
}
</style>
