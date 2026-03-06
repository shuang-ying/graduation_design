"""
监控模块路由
处理摄像头和录像相关的 API 请求
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
from pathlib import Path

from models import Camera, Recording
from services.camera_service import CameraService
from services.recording_service import RecordingService
from services.stream_service import StreamService


router = APIRouter(prefix="/api", tags=["监控系统"])

# 服务实例
camera_service = CameraService()
recording_service = RecordingService()
stream_service = StreamService()


# -------------------------- Pydantic 数据模型 --------------------------

class CameraCreate(BaseModel):
    """创建摄像头请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="摄像头名称")
    rtsp_url: str = Field(..., min_length=1, max_length=500, description="RTSP 流地址")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")


class CameraUpdate(BaseModel):
    """更新摄像头请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="摄像头名称")
    rtsp_url: Optional[str] = Field(None, min_length=1, max_length=500, description="RTSP 流地址")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    status: Optional[bool] = Field(None, description="是否在线")


class RecordingCreate(BaseModel):
    """创建录像请求模型"""
    duration: int = Field(default=60, ge=1, le=600, description="录像时长（秒）")


# -------------------------- 摄像头管理接口 --------------------------

@router.get("/cameras", summary="获取所有摄像头列表", response_model=List[dict])
async def get_all_cameras():
    """获取所有摄像头的信息"""
    try:
        cameras = await camera_service.get_all_cameras()
        
        # 转换为字典列表
        camera_list = []
        for camera in cameras:
            camera_dict = {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "status": camera.status,
                "location": camera.location,
                "created_time": camera.created_time.isoformat() if camera.created_time else None,
                "last_active_time": camera.last_active_time.isoformat() if camera.last_active_time else None,
                "is_recording": recording_service.get_active_recording(camera.id)
            }
            camera_list.append(camera_dict)
        
        return camera_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摄像头列表失败：{str(e)}")


@router.get("/cameras/{camera_id}", summary="获取单个摄像头详情", response_model=dict)
async def get_camera(camera_id: int):
    """获取指定摄像头的详细信息"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    return {
        "id": camera.id,
        "name": camera.name,
        "rtsp_url": camera.rtsp_url,
        "status": camera.status,
        "location": camera.location,
        "created_time": camera.created_time.isoformat() if camera.created_time else None,
        "last_active_time": camera.last_active_time.isoformat() if camera.last_active_time else None,
        "is_recording": recording_service.get_active_recording(camera.id)
    }


@router.post("/cameras", summary="添加摄像头", status_code=status.HTTP_201_CREATED)
async def create_camera(camera_info: CameraCreate):
    """添加新的摄像头"""
    # 检查名称是否已存在
    if await camera_service.check_camera_exists(camera_info.name):
        raise HTTPException(status_code=400, detail="摄像头名称已存在")
    
    try:
        camera = await camera_service.create_camera(
            name=camera_info.name,
            rtsp_url=camera_info.rtsp_url,
            location=camera_info.location
        )
        
        return {
            "code": 201,
            "message": "摄像头添加成功",
            "data": {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "location": camera.location
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加摄像头失败：{str(e)}")


@router.put("/cameras/{camera_id}", summary="更新摄像头信息")
async def update_camera(camera_id: int, camera_info: CameraUpdate):
    """更新摄像头的信息"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    # 如果修改了名称，检查新名称是否已被使用
    if camera_info.name and camera_info.name != camera.name:
        if await camera_service.check_camera_exists(camera_info.name):
            raise HTTPException(status_code=400, detail="摄像头名称已存在")
    
    try:
        updated_camera = await camera_service.update_camera(
            camera_id=camera_id,
            name=camera_info.name,
            rtsp_url=camera_info.rtsp_url,
            location=camera_info.location,
            status=camera_info.status
        )
        
        return {
            "code": 200,
            "message": "摄像头更新成功",
            "data": {
                "id": updated_camera.id,
                "name": updated_camera.name,
                "rtsp_url": updated_camera.rtsp_url,
                "location": updated_camera.location,
                "status": updated_camera.status
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新摄像头失败：{str(e)}")


@router.delete("/cameras/{camera_id}", summary="删除摄像头")
async def delete_camera(camera_id: int):
    """删除指定的摄像头"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    # 如果摄像头正在录像，不允许删除
    if recording_service.get_active_recording(camera_id):
        raise HTTPException(status_code=400, detail="摄像头正在录像，无法删除")
    
    try:
        success = await camera_service.delete_camera(camera_id)
        
        if success:
            return {"code": 200, "message": "摄像头删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除摄像头失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除摄像头失败：{str(e)}")


@router.get("/cameras/{camera_id}/status", summary="获取摄像头状态")
async def get_camera_status(camera_id: int):
    """获取摄像头的在线状态和录像状态"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    return {
        "id": camera.id,
        "name": camera.name,
        "status": camera.status,
        "is_recording": recording_service.get_active_recording(camera_id),
        "last_active_time": camera.last_active_time.isoformat() if camera.last_active_time else None
    }


# -------------------------- 视频流接口 --------------------------

@router.get("/stream/{camera_id}", summary="获取摄像头直播流")
async def get_stream(camera_id: int):
    """获取摄像头的实时视频流（MJPEG 格式）"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    try:
        # 返回 MJPEG 流
        return StreamingResponse(
            stream_service.get_stream_frame(camera.rtsp_url, camera_id),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Pragma": "no-cache"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频流获取失败：{str(e)}")


@router.get("/stream/{camera_id}/test", summary="测试摄像头连接")
async def test_camera_connection(camera_id: int):
    """测试摄像头 RTSP 流是否可连接"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    try:
        is_available = await stream_service.check_stream_availability(camera.rtsp_url)
        
        if is_available:
            # 更新摄像头状态为在线
            await camera_service.update_camera_status(camera_id, True)
            return {"code": 200, "message": "摄像头连接正常", "available": True}
        else:
            await camera_service.update_camera_status(camera_id, False)
            return {"code": 200, "message": "摄像头无法连接", "available": False}
    
    except Exception as e:
        await camera_service.update_camera_status(camera_id, False)
        raise HTTPException(status_code=500, detail=f"测试连接失败：{str(e)}")


# -------------------------- 录像管理接口 --------------------------

@router.post("/recordings/start/{camera_id}", summary="开始录像", status_code=status.HTTP_201_CREATED)
async def start_recording(camera_id: int, recording_info: Optional[RecordingCreate] = None):
    """开始录制指定摄像头的视频"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    # 检查是否已经在录像
    if recording_service.get_active_recording(camera_id):
        raise HTTPException(status_code=400, detail="摄像头正在录像中")
    
    duration = recording_info.duration if recording_info else 60
    
    try:
        recording = await recording_service.start_recording(camera, duration)
        
        if recording:
            return {
                "code": 201,
                "message": f"开始录像，预计录制{duration}秒",
                "data": {
                    "recording_id": recording.id,
                    "camera_id": camera_id,
                    "start_time": recording.start_time.isoformat(),
                    "expected_duration": duration
                }
            }
        else:
            raise HTTPException(status_code=500, detail="开始录像失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始录像失败：{str(e)}")


@router.post("/recordings/stop/{camera_id}", summary="停止录像")
async def stop_recording(camera_id: int):
    """停止录制指定摄像头的视频"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    # 检查是否在录像
    if not recording_service.get_active_recording(camera_id):
        raise HTTPException(status_code=400, detail="摄像头未在录像")
    
    try:
        success = await recording_service.stop_recording(camera_id)
        
        if success:
            # 手动更新摄像头状态为未录像
            camera.status = True  # 保持在线状态
            camera.last_active_time = datetime.now()
            await camera.save()
            
            return {"code": 200, "message": "录像已停止"}
        else:
            raise HTTPException(status_code=500, detail="停止录像失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止录像失败：{str(e)}")


@router.get("/recordings/camera/{camera_id}", summary="获取某摄像头的所有录像", response_model=List[dict])
async def get_recordings_by_camera(camera_id: int):
    """获取指定摄像头的所有录像记录"""
    camera = await camera_service.get_camera_by_id(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    try:
        recordings = await Recording.filter(camera_id=camera_id).order_by("-start_time")
        
        recording_list = []
        for recording in recordings:
            recording_dict = {
                "id": recording.id,
                "camera_id": recording.camera_id,
                "file_path": recording.file_path,
                "start_time": recording.start_time.isoformat() if recording.start_time else None,
                "end_time": recording.end_time.isoformat() if recording.end_time else None,
                "duration": recording.duration,
                "file_size": recording.file_size,
                "created_time": recording.created_time.isoformat() if recording.created_time else None
            }
            recording_list.append(recording_dict)
        
        return recording_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取录像列表失败：{str(e)}")


@router.get("/recordings/{recording_id}", summary="获取录像详情", response_model=dict)
async def get_recording(recording_id: int):
    """获取指定录像的详细信息"""
    recording = await recording_service.get_recording_by_id(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像记录不存在")
    
    return {
        "id": recording.id,
        "camera_id": recording.camera_id,
        "file_path": recording.file_path,
        "start_time": recording.start_time.isoformat() if recording.start_time else None,
        "end_time": recording.end_time.isoformat() if recording.end_time else None,
        "duration": recording.duration,
        "file_size": recording.file_size,
        "created_time": recording.created_time.isoformat() if recording.created_time else None
    }


@router.get("/recordings/{recording_id}/play", summary="播放录像文件")
async def play_recording(recording_id: int):
    """播放指定的录像文件"""
    recording = await recording_service.get_recording_by_id(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像记录不存在")
    
    # 检查文件是否存在
    if not os.path.exists(recording.file_path):
        raise HTTPException(status_code=404, detail="录像文件不存在")
    
    return FileResponse(
        recording.file_path,
        media_type="video/mp4",
        filename=os.path.basename(recording.file_path)
    )


@router.delete("/recordings/{recording_id}", summary="删除录像")
async def delete_recording(recording_id: int):
    """删除指定的录像记录"""
    recording = await recording_service.get_recording_by_id(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像记录不存在")
    
    try:
        success = await recording_service.delete_recording(recording_id)
        
        if success:
            return {"code": 200, "message": "录像删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除录像失败")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除录像失败：{str(e)}")
