// 监控状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMonitorStore = defineStore('monitor', () => {
  // 当前选中的摄像头 ID
  const currentCameraId = ref(null)
  
  // 当前选中的摄像头信息
  const currentCamera = ref(null)
  
  // 正在录像的摄像头 ID 列表
  const recordingCameras = ref([])
  
  // 录像时长（秒）
  const recordingDuration = ref(60)
  
  // 设置当前摄像头
  const setCurrentCamera = (camera) => {
    currentCameraId.value = camera?.id || null
    currentCamera.value = camera || null
  }
  
  // 添加正在录像的摄像头
  const addRecordingCamera = (cameraId) => {
    if (!recordingCameras.value.includes(cameraId)) {
      recordingCameras.value.push(cameraId)
    }
  }
  
  // 移除正在录像的摄像头
  const removeRecordingCamera = (cameraId) => {
    const index = recordingCameras.value.indexOf(cameraId)
    if (index > -1) {
      recordingCameras.value.splice(index, 1)
    }
  }
  
  // 检查摄像头是否在录像
  const isRecording = (cameraId) => {
    return recordingCameras.value.includes(cameraId)
  }
  
  // 设置录像时长
  const setRecordingDuration = (duration) => {
    recordingDuration.value = duration
  }
  
  // 清空所有状态
  const reset = () => {
    currentCameraId.value = null
    currentCamera.value = null
    recordingCameras.value = []
    recordingDuration.value = 60
  }
  
  return {
    currentCameraId,
    currentCamera,
    recordingCameras,
    recordingDuration,
    setCurrentCamera,
    addRecordingCamera,
    removeRecordingCamera,
    isRecording,
    setRecordingDuration,
    reset
  }
})
