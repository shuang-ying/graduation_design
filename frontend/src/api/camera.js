import request from '@/utils/request'

/**
 * 获取所有摄像头列表
 */
export function getCameras() {
  return request.get('/cameras')
}

/**
 * 获取单个摄像头详情
 * @param {number} cameraId - 摄像头 ID
 */
export function getCamera(cameraId) {
  return request.get(`/cameras/${cameraId}`)
}

/**
 * 添加摄像头
 * @param {Object} data - 摄像头信息
 * @param {string} data.name - 摄像头名称
 * @param {string} data.rtsp_url - RTSP 流地址
 * @param {string} data.location - 安装位置
 */
export function addCamera(data) {
  return request.post('/cameras', data)
}

/**
 * 更新摄像头信息
 * @param {number} cameraId - 摄像头 ID
 * @param {Object} data - 摄像头信息
 */
export function updateCamera(cameraId, data) {
  return request.put(`/cameras/${cameraId}`, data)
}

/**
 * 删除摄像头
 * @param {number} cameraId - 摄像头 ID
 */
export function deleteCamera(cameraId) {
  return request.delete(`/cameras/${cameraId}`)
}

/**
 * 获取摄像头状态
 * @param {number} cameraId - 摄像头 ID
 */
export function getCameraStatus(cameraId) {
  return request.get(`/cameras/${cameraId}/status`)
}

/**
 * 测试摄像头连接
 * @param {number} cameraId - 摄像头 ID
 */
export function testCameraConnection(cameraId) {
  return request.get(`/stream/${cameraId}/test`)
}

/**
 * 获取实时视频流地址（MJPEG 格式，更稳定）
 * @param {number} cameraId - 摄像头 ID
 */
export function getStreamUrl(cameraId) {
  return `http://localhost:8000/api/video/${cameraId}`
}
