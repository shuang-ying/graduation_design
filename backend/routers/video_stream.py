"""
监控模块路由 - 视频流专用
提供稳定的 MJPEG 视频流
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import cv2
import asyncio
import logging

from models import Camera
from services.camera_service import CameraService

router = APIRouter(prefix="/api", tags=["视频流"])

camera_service = CameraService()
logger = logging.getLogger(__name__)


async def generate_mjpeg_stream(rtsp_url: str, camera_id: int) -> AsyncGenerator[bytes, None]:
    """
    生成 MJPEG 视频流（流畅优先版）
    :param rtsp_url: RTSP 流地址
    :param camera_id: 摄像头 ID
    """
    cap = None
    
    try:
        # 打开 RTSP 流，使用 FFmpeg 后端
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            logger.error(f"无法打开 RTSP 流：{rtsp_url}")
            return
        
        # 优化参数设置 - 流畅优先
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 最小缓冲区，降低延迟
        cap.set(cv2.CAP_PROP_FPS, 20)  # 降低目标帧率到 20
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 降低分辨率到 640
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 降低分辨率到 480
        
        # 获取实际帧率
        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        frame_delay = 1.0 / min(fps, 20)  # 最大 20fps
        
        logger.info(f"视频流已启动 (camera {camera_id}), FPS={fps:.2f}, 分辨率：640x480")
        
        skip_frames = 0  # 跳帧计数器
        
        while True:
            ret, frame = cap.read()
            
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue
            
            # 跳帧策略：每 3 帧发送 1 帧（只发送 33% 的帧）
            skip_frames += 1
            if skip_frames < 3:
                continue
            skip_frames = 0
            
            # 编码为 JPEG（质量 45，大幅降低画质提升流畅度）
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 45]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                continue
            
            # 生成 MJPEG 帧
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
            )
            
            # 根据帧率动态调整延迟
            await asyncio.sleep(frame_delay)
    
    except Exception as e:
        logger.error(f"视频流错误 (camera {camera_id}): {e}")
    finally:
        if cap:
            cap.release()


@router.get("/video/{camera_id}")
async def get_video_stream(camera_id: int):
    """
    获取摄像头实时视频流（MJPEG 格式）
    可以直接在 img 标签或 video 组件中使用
    """
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    return StreamingResponse(
        generate_mjpeg_stream(camera.rtsp_url, camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Access-Control-Allow-Origin": "*",
        }
    )
