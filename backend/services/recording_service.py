"""
录像服务层
处理录像相关的业务逻辑
"""
from typing import List, Optional
from models import Camera, Recording
from datetime import datetime
import os
import asyncio
import cv2
from pathlib import Path
from services.camera_service import CameraService


class RecordingService:
    """录像服务类"""
    
    # 录像存储目录
    RECORDINGS_DIR = Path("backend/static/recordings")
    
    def __init__(self):
        self.active_recordings = {}  # 存储正在进行的录像任务 {camera_id: task}
    
    @staticmethod
    async def get_recordings_by_camera(camera_id: int) -> List[Recording]:
        """获取指定摄像头的所有录像"""
        recordings = await Recording.filter(camera_id=camera_id).order_by("-start_time")
        return recordings
    
    @staticmethod
    async def get_recording_by_id(recording_id: int) -> Optional[Recording]:
        """根据 ID 获取录像"""
        recording = await Recording.filter(id=recording_id).first()
        return recording
    
    @staticmethod
    async def create_recording(
        camera_id: int,
        file_path: str,
        start_time: datetime
    ) -> Recording:
        """创建录像记录"""
        recording = await Recording.create(
            camera_id=camera_id,
            file_path=file_path,
            start_time=start_time,
            duration=0,
            file_size=0
        )
        return recording
    
    @staticmethod
    async def update_recording(
        recording_id: int,
        end_time: datetime,
        duration: int,
        file_size: int
    ) -> Optional[Recording]:
        """更新录像记录（结束录像时使用）"""
        recording = await Recording.filter(id=recording_id).first()
        if not recording:
            return None
        
        recording.end_time = end_time
        recording.duration = duration
        recording.file_size = file_size
        await recording.save()
        return recording
    
    @staticmethod
    async def delete_recording(recording_id: int) -> bool:
        """删除录像记录"""
        recording = await Recording.filter(id=recording_id).first()
        if not recording:
            return False
        
        # 删除文件
        try:
            if os.path.exists(recording.file_path):
                os.remove(recording.file_path)
        except Exception as e:
            print(f"删除录像文件失败：{e}")
        
        # 删除数据库记录
        await Recording.filter(id=recording_id).delete()
        return True
    
    async def start_recording(
        self,
        camera: Camera,
        duration: int = 60
    ) -> Optional[Recording]:
        """
        开始录像
        :param camera: 摄像头对象
        :param duration: 录像时长（秒），默认 60 秒
        :return: 录像记录对象
        """
        try:
            # 确保目录存在
            self.RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"camera_{camera.id}_{timestamp}.mp4"
            filepath = self.RECORDINGS_DIR / filename
            
            # 创建数据库记录
            recording = await self.create_recording(
                camera_id=camera.id,
                file_path=str(filepath),
                start_time=datetime.now()
            )
            
            # 启动录像任务
            task = asyncio.create_task(
                self._record_video(camera.rtsp_url, str(filepath), duration, recording.id)
            )
            self.active_recordings[camera.id] = task
            
            # 更新摄像头状态
            await CameraService.update_camera_status(camera.id, True)
            
            return recording
        except Exception as e:
            print(f"开始录像失败：{e}")
            return None
    
    async def stop_recording(self, camera_id: int) -> bool:
        """
        停止录像
        :param camera_id: 摄像头 ID
        :return: 是否成功停止
        """
        if camera_id not in self.active_recordings:
            return False
        
        # 取消任务
        task = self.active_recordings[camera_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.active_recordings[camera_id]
        
        # 更新摄像头状态
        await CameraService.update_camera_status(camera_id, False)
        
        return True
    
    async def _record_video(
        self,
        rtsp_url: str,
        output_path: str,
        duration: int,
        recording_id: int
    ):
        """
        实际录制视频的方法（优化版）
        :param rtsp_url: RTSP 流地址
        :param output_path: 输出文件路径
        :param duration: 录制时长（秒）
        :param recording_id: 录像记录 ID
        """
        cap = None
        out = None
        retry_count = 0
        max_retries = 3
        
        try:
            # 确保目录存在
            self.RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
            
            # 打开 RTSP 流，带重试机制
            while retry_count < max_retries:
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                
                if cap.isOpened():
                    break
                
                retry_count += 1
                print(f"打开 RTSP 流失败，第 {retry_count} 次重试...")
                await asyncio.sleep(2)
            
            if not cap.isOpened():
                raise Exception(f"无法打开 RTSP 流，已重试{max_retries}次")
            
            # 获取视频参数
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
            
            print(f"开始录像：{output_path}, FPS={fps:.2f}, 分辨率={width}x{height}")
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise Exception("无法创建视频写入器")
            
            start_time = datetime.now()
            frame_count = 0
            error_count = 0
            max_errors = 10
            
            # 录制视频
            while True:
                # 检查是否超时（允许 2 秒误差）
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= duration + 2:
                    break
                
                # 读取帧
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    error_count += 1
                    if error_count > max_errors:
                        print(f"连续读取失败{error_count}次，尝试重连...")
                        cap.release()
                        await asyncio.sleep(1)
                        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                        error_count = 0
                    await asyncio.sleep(0.1)
                    continue
                
                # 重置错误计数
                error_count = 0
                frame_count += 1
                
                # 写入帧
                out.write(frame)
                
                # 每 10 秒打印进度
                if frame_count % int(fps * 10) == 0:
                    print(f"录像进度：{int(elapsed)}/{duration}秒，帧数：{frame_count}")
                
                # 短暂等待
                await asyncio.sleep(0.01)
            
            # 释放资源
            if out:
                out.release()
                out = None
            
            if cap:
                cap.release()
                cap = None
            
            # 获取文件大小
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            # 更新数据库记录
            end_time = datetime.now()
            actual_duration = int((end_time - start_time).total_seconds())
            
            await self.update_recording(
                recording_id=recording_id,
                end_time=end_time,
                duration=actual_duration,
                file_size=file_size
            )
            
            print(f"✅ 录像完成：{output_path}, 时长：{actual_duration}秒，帧数：{frame_count}, 大小：{file_size/1024:.1f}KB")
            
            # 录像完成后，更新摄像头状态为未录像
            try:
                camera = await Camera.filter(id=camera_id).first()
                if camera:
                    camera.status = True  # 摄像头在线
                    camera.last_active_time = datetime.now()
                    await camera.save()
                    print(f"✅ 摄像头 {camera_id} 状态已更新：录像结束")
            except Exception as e:
                print(f"更新摄像头状态失败：{e}")
            
        except Exception as e:
            print(f"❌ 录像过程中出错：{e}")
            
            # 清理资源
            if out:
                out.release()
            if cap:
                cap.release()
            
            # 删除不完整的文件
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"已删除不完整的文件：{output_path}")
            except Exception as e:
                print(f"删除文件失败：{e}")
        
        finally:
            # 确保资源被释放
            if out:
                out.release()
            if cap:
                cap.release()
    
    def get_active_recording(self, camera_id: int) -> bool:
        """检查摄像头是否正在录像"""
        return camera_id in self.active_recordings
