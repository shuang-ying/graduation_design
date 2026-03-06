from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import User


# -------------------------- 基础配置 --------------------------
# 1. 应用初始化
app=FastAPI(title="毕业设计后端",version="1.0.0")

# 2. 跨域配置（解决前端请求后端的跨域拦截）
origins = [
    "http://localhost:5173",  # Vue3 默认端口，必须和前端实际端口一致
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许这些前端域名访问
    allow_credentials=True,  # 允许前端携带 cookie（比如后续记住登录）
    allow_methods=["*"],  # 允许所有请求方法（GET/POST/PUT 等）
    allow_headers=["*"],  # 允许所有请求头（比如 Authorization 携带 token）
)

# 3. JWT 核心配置
SECRET_KEY = "graduation_design_bupt_lrh_2022211610"  # 加密密钥：生产环境要换成随机字符串（比如 openssl rand -hex 32 生成）
ALGORITHM = "HS256"  # 加密算法：HS256 是对称加密（前后端用同一个密钥）
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # token 有效期 30 分钟（过期后需要重新登录）

# -------------------------- Pydantic 数据验证模型 --------------------------
# 1. 注册请求体验证：前端传的参数必须符合这个规则，否则直接返回错误
class RegisterRequest(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    confirm_password: str

    # 验证1：两次密码一致【修改点1：移除 @classmethod】
    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        # info.data 是请求体的所有数据（Pydantic v2 写法）
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

    # 验证2：密码长度校验【修改点2：移除 @classmethod】
    @field_validator("password")
    def password_length_check(cls, v):
        # 检查字节长度（utf-8 编码）
        password_bytes = v.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError("密码过长，最多支持72字节（约24个中文/72个英文）")
        if len(v) < 6:
            raise ValueError("密码过短，至少需要6位")
        return v
    
# 2. 登录请求体验证：只需要用户名和密码
class LoginRequest(BaseModel):
    username: str
    password: str

# 3. 登录返回数据模型：规定返回给前端的格式（自动校验，避免返回格式混乱）
class TokenResponse(BaseModel):
    access_token: str  # JWT token 字符串
    token_type: str = "bearer"  # token 类型（固定为 bearer，前端请求时要加在 Authorization 头里）
    username: str  # 返回用户名，方便前端显示

# -------------------------- 核心工具函数 --------------------------
# 生成 JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # data：要存储到 token 里的信息（比如 {"sub": "zhangsan"}，sub 是 JWT 标准字段，代表用户标识）
    to_encode = data.copy()  # 复制数据，避免修改原字典
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # utcnow() 是 UTC 时间，避免时区问题
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 默认 15 分钟过期
    to_encode.update({"exp": expire})  # 把过期时间加入 payload
    # 生成 JWT token：用 SECRET_KEY 和 HS256 算法加密
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------------- 接口路由 --------------------------
# 1. 注册接口：POST 请求，路径 /api/register，summary 是接口文档的描述
@app.post("/api/register", summary="用户注册")
async def register(user_info: RegisterRequest):  # 自动校验前端传的参数，不符合则返回 422 错误
    # 步骤1：检查用户名是否已存在（异步查询，await 必须加，否则会阻塞）
    existing_user = await User.filter(username=user_info.username).first()
    if existing_user:
        # 抛出 400 错误（Bad Request），detail 是错误信息，前端能捕获
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 步骤2：加密密码（调用 User 类的 hash_password 方法）
    hashed_password = User.hash_password(user_info.password)
    
    # 步骤3：创建用户（写入数据库，异步操作）
    await User.create(
        username=user_info.username,
        email=user_info.email,
        password=hashed_password  # 只存加密后的密码，不存明文！
    )
    
    # 返回成功信息（前端根据 code 判断是否成功）
    return {"code": 200, "message": "注册成功"}

# 2. 登录接口：POST 请求，路径 /api/login，response_model 指定返回格式
@app.post("/api/login", summary="用户登录", response_model=TokenResponse)
async def login(login_info: LoginRequest):
    # 步骤1：检查用户是否存在
    user = await User.filter(username=login_info.username).first()
    if not user:
        # 不直接提示“用户不存在”，而是“用户名或密码错误”，防止黑客枚举用户名
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 步骤2：验证密码（明文密码 vs 数据库中的加密密码）
    if not User.verify_password(login_info.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 步骤3：生成 token（有效期 30 分钟）
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # token 里存储用户名
        expires_delta=access_token_expires
    )
    
    # 返回 token、类型、用户名（符合 TokenResponse 模型）
    return {"access_token": access_token, "username": user.username}


#注册orm
register_tortoise(
    app,  # 关联 FastAPI 应用
    # 数据库连接字符串：mysql://用户名:密码@主机:端口/数据库名
    db_url="mysql://root:123456@localhost:3306/graduation_design",
    modules={"models": ["models"]},  # 告诉 Tortoise 加载哪个文件的模型
    generate_schemas=True,  # 开发环境：自动创建表（生产环境要关闭，手动建表更安全）
    add_exception_handlers=True,  # 添加数据库异常处理（比如连接失败时返回友好错误）
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000,host="0.0.0.0")