from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:xhnmdl0407@localhost/elderly_health_db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出连接池大小后可打开的连接数
    pool_timeout=30,  # 获取连接的超时时间(秒)
    pool_recycle=3600,  # 连接回收时间(秒)
    echo=True  # 显示SQL日志(调试用)
)

# 创建本地会话类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()