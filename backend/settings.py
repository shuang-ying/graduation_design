TORTOISE_ORM = {
    "connections": {
        # MySQL 配置（替换为你的实际信息）
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",       # 你的 MySQL 用户名
                "password": "123456", # 你的 MySQL 密码
                "database": "graduation_design", # 提前创建的数据库名
                "charset": "utf8mb4",
            }
        }
        # 若用 SQLite（无需安装 aiomysql），替换为：
        # "default": "sqlite://./student.db"
    },
    "apps": {
        "models": {
            "models": ["models"],  # 模型文件路径
            "default_connection": "default",
        }
    },
    "use_tz": False,  # 不使用 UTC 时间
    "timezone": "Asia/Shanghai"  # 设置时区为东八区
}