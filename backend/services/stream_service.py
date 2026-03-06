"""
视频流服务层（合并优化版）
使用 OpenCV 捕获 RTSP 流并提供稳定的 MJPEG 流
"""
import cv2
import asyncio
from typing import Optional, AsyncGenerator
from models import Camera
from datetime import datetime
import logging

# 配置日志，屏蔽 FFmpeg 的解码错误
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger('asyncio').setLevel(logging.WARNING)


class StreamService:
    """视频流服务类"""
    
    def __init__(self):
        self.active_streams = {}  # 存储活跃的视频流 {camera_id: cap}
    
    async def get_stream_frame(
        self,
        rtsp_url: str,
        camera_id: int
    ) -> AsyncGenerator[bytes, None]:
        """
        获取视频流帧（MJPEG 格式，优化版）
        :param rtsp_url: RTSP 流地址
        :param camera_id: 摄像头 ID
        :yield: JPEG 格式的视频帧
        """
        cap = None
        
        try:
            # 打开 RTSP 流，使用 FFmpeg 后端
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            
            if not cap.isOpened():
                logger.error(f"无法打开 RTSP 流：{rtsp_url}")
                raise Exception(f"无法打开 RTSP 流")
            
            # 设置优化参数
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减小缓冲区，降低延迟
            cap.set(cv2.CAP_PROP_FPS, 20)  # 目标帧率
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)  # 超时设置
            
            # 获取实际帧率
            fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
            frame_delay = 1.0 / min(fps, 20)  # 最大 20fps
            
            logger.info(f"视频流已启动 (camera {camera_id}), FPS={fps:.2f}")
            
            self.active_streams[camera_id] = cap
            
            error_count = 0
            max_errors = 10  # 最多允许连续 10 次错误
            frame_count = 0
            
            while camera_id in self.active_streams:
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    error_count += 1
                    if error_count > max_errors:
                        logger.warning(f"视频流连续错误 {error_count} 次，重连中... (camera {camera_id})")
                        # 尝试重新打开
                        cap.release()
                        await asyncio.sleep(2)
                        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                        error_count = 0
                    else:
                        await asyncio.sleep(0.5)
                    continue
                
                # 重置错误计数
                error_count = 0
                frame_count += 1
                
                # 编码为 JPEG（质量 60，平衡质量和速度）
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                if not ret:
                    logger.warning(f"编码失败 (camera {camera_id})")
                    continue
                
                # 生成 MJPEG 格式的帧
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
                )
                
                # 控制帧率
                await asyncio.sleep(frame_delay)
            
            logger.info(f"视频流已停止 (camera {camera_id})")
            
        except Exception as e:
            # 忽略常见的解码错误
            error_msg = str(e)
            ignore_errors = [
                "Missing reference picture",
                "decode_slice_header error",
                "mb_type",
                "P sub_mb_type",
                "negative number of zero coeffs",
                "out of range intra chroma pred mode",
                "corrupted macroblock"
            ]
            
            should_print = True
            for ignore in ignore_errors:
                if ignore in error_msg:
                    should_print = False
                    break
            
            if should_print:
                logger.error(f"视频流错误 (camera {camera_id}): {e}")
        finally:
            if cap:
                cap.release()
            if camera_id in self.active_streams:
                del self.active_streams[camera_id]
    
    def stop_stream(self, camera_id: int):
        """停止视频流"""
        if camera_id in self.active_streams:
            cap = self.active_streams[camera_id]
            cap.release()
            del self.active_streams[camera_id]
    
    async def check_stream_availability(self, rtsp_url: str) -> bool:
        """
        检查 RTSP 流是否可用
        :param rtsp_url: RTSP 流地址
        :return: 是否可用
        """
        cap = None
        
        try:
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                return ret
            
            return False
        
        except Exception as e:
            logger.error(f"检查视频流失败：{e}")
            return False
        
        finally:
            if cap:
                cap.release()
