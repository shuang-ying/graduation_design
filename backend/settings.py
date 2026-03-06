TORTOISE_ORM = {
    "connections": {
            "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                            "host": "localhost",
                            "port": "3306",
                            "user": "root",
                            "password": "123456",
                            "database": "graduation_design",
                            "minsize": 1,
                            "maxsize": 10,
                            "charset": "utf8mb4",
                            "echo": True,
                    },
            },
    },
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "Asia/Shanghai",
}