"""
摄像头服务层
处理摄像头相关的业务逻辑
"""
from typing import List, Optional
from models import Camera
from datetime import datetime


class CameraService:
    """摄像头服务类"""
    
    @staticmethod
    async def get_all_cameras() -> List[Camera]:
        """获取所有摄像头"""
        cameras = await Camera.all().order_by("-created_time")
        return cameras
    
    @staticmethod
    async def get_camera_by_id(camera_id: int) -> Optional[Camera]:
        """根据 ID 获取摄像头"""
        camera = await Camera.filter(id=camera_id).first()
        return camera
    
    @staticmethod
    async def create_camera(
        name: str,
        rtsp_url: str,
        location: Optional[str] = None
    ) -> Camera:
        """创建摄像头"""
        camera = await Camera.create(
            name=name,
            rtsp_url=rtsp_url,
            location=location,
            status=False
        )
        return camera
    
    @staticmethod
    async def update_camera(
        camera_id: int,
        name: Optional[str] = None,
        rtsp_url: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[bool] = None
    ) -> Optional[Camera]:
        """更新摄像头信息"""
        camera = await Camera.filter(id=camera_id).first()
        if not camera:
            return None
        
        if name is not None:
            camera.name = name
        if rtsp_url is not None:
            camera.rtsp_url = rtsp_url
        if location is not None:
            camera.location = location
        if status is not None:
            camera.status = status
        
        await camera.save()
        return camera
    
    @staticmethod
    async def delete_camera(camera_id: int) -> bool:
        """删除摄像头"""
        deleted_count = await Camera.filter(id=camera_id).delete()
        return deleted_count > 0
    
    @staticmethod
    async def update_camera_status(camera_id: int, status: bool) -> Optional[Camera]:
        """更新摄像头状态"""
        camera = await Camera.filter(id=camera_id).first()
        if not camera:
            return None
        
        camera.status = status
        camera.last_active_time = datetime.now()
        await camera.save()
        return camera
    
    @staticmethod
    async def check_camera_exists(name: str) -> bool:
        """检查摄像头名称是否存在"""
        exists = await Camera.filter(name=name).exists()
        return exists
