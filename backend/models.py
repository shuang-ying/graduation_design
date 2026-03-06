##数据库模型

from tortoise import fields, models
from passlib.context import CryptContext

# 密码加密上下文（指定 bcrypt 算法）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(models.Model):
    """用户表模型"""
    id = fields.IntField(pk=True, auto_increment=True)  # 主键，自增
    username = fields.CharField(max_length=50, unique=True)  # 用户名，唯一
    email = fields.CharField(max_length=100, null=True)  # 邮箱，可选
    password = fields.CharField(max_length=100)  # 存储加密后的密码（不是明文）
    created_time = fields.DatetimeField(auto_now_add=True)  # 创建时间，自动填充

    class Meta:
        table = "users"  # 数据库中表名
        table_description = "用户表"
    
        # 密码加密方法
    @classmethod # 类方法，用于密码加密
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)
    
        # 密码验证方法
    @classmethod # 类方法，用于密码验证
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class Camera(models.Model):
    """摄像头表模型"""
    id = fields.IntField(pk=True, auto_increment=True)  # 主键，自增
    name = fields.CharField(max_length=100, unique=True)  # 摄像头名称，唯一
    rtsp_url = fields.CharField(max_length=500)  # RTSP 流地址
    status = fields.BooleanField(default=True)  # 是否在线
    location = fields.CharField(max_length=200, null=True)  # 安装位置
    created_time = fields.DatetimeField(auto_now_add=True)  # 创建时间
    last_active_time = fields.DatetimeField(null=True)  # 最后活跃时间
    
    # 关联录像
    recordings: fields.ReverseRelation["Recording"]
    
    class Meta:
        table = "cameras"  # 数据库中表名
        table_description = "摄像头表"


class Recording(models.Model):
    """录像文件表模型"""
    id = fields.IntField(pk=True, auto_increment=True)  # 主键，自增
    camera = fields.ForeignKeyField(
        "models.Camera", 
        related_name="recordings",
        on_delete=fields.CASCADE
    )  # 外键，关联摄像头
    file_path = fields.CharField(max_length=500)  # 录像文件存储路径
    start_time = fields.DatetimeField()  # 录像开始时间
    end_time = fields.DatetimeField(null=True)  # 录像结束时间
    duration = fields.IntField(default=0)  # 录像时长（秒）
    file_size = fields.BigIntField(default=0)  # 文件大小（字节）
    created_time = fields.DatetimeField(auto_now_add=True)  # 创建时间
    
    class Meta:
        table = "recordings"  # 数据库中表名
        table_description = "录像文件表"