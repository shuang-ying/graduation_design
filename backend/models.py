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