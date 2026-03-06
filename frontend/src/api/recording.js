import request from '@/utils/request'

/**
 * 开始录像
 * @param {number} cameraId - 摄像头 ID
 * @param {number} duration - 录像时长（秒）
 */
export function startRecording(cameraId, duration = 60) {
  return request.post(`/recordings/start/${cameraId}`, { duration })
}

/**
 * 停止录像
 * @param {number} cameraId - 摄像头 ID
 */
export function stopRecording(cameraId) {
  return request.post(`/recordings/stop/${cameraId}`)
}

/**
 * 获取某摄像头的所有录像
 * @param {number} cameraId - 摄像头 ID
 */
export function getRecordingsByCamera(cameraId) {
  return request.get(`/recordings/camera/${cameraId}`)
}

/**
 * 获取录像详情
 * @param {number} recordingId - 录像 ID
 */
export function getRecording(recordingId) {
  return request.get(`/recordings/${recordingId}`)
}

/**
 * 删除录像
 * @param {number} recordingId - 录像 ID
 */
export function deleteRecording(recordingId) {
  return request.delete(`/recordings/${recordingId}`)
}

/**
 * 获取录像播放地址
 * @param {number} recordingId - 录像 ID
 */
export function getRecordingPlayUrl(recordingId) {
  return `http://localhost:8000/api/recordings/${recordingId}/play`
}
