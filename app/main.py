from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from app.database import Base, engine
from app.routers import follow_up
import logging

from app.routers.follow_up import get_db
# 在main.py中添加
from app.database import Base, engine
# Base.metadata.drop_all(bind=engine)  # 删除旧表
# Base.metadata.create_all(bind=engine)  # 创建新表
# 在 main.py 的 lifespan 或启动代码中添加
from app.models import Elderly, Doctor, FollowUp  # 显式导入所有模型

# # 确保表完全重建
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
# 在 main.py 中添加
import os

# 设置工作目录为项目根目录
project_root = Path(__file__).parent.parent
os.chdir(project_root)
print(f"当前工作目录: {os.getcwd()}")
# 启用SQLAlchemy调试日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 显示所有SQL查询和参数
app = FastAPI()

# 创建静态文件目录（如果不存在）
static_dir = Path("static")
os.makedirs(static_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("elderly"):
            Base.metadata.create_all(bind=engine)
    yield
    # 关闭时可以添加清理逻辑


app = FastAPI(
    title="老年人健康管理平台",
    version="1.0.0",
    description="老年人健康随访管理系统",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许的源，这里假设前端运行在 http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含路由
app.include_router(
    follow_up.router,
    prefix="/api/v1",
    tags=["随访管理"]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",  # 关键修改点
        host="localhost",
        port=8000,
        reload=True
    )


@app.get("/debug/db_config")
def debug_db_config(db: Session = Depends(get_db)):
    return {
        "db_url": str(db.bind.url),  # 显示实际连接字符串
        "pool_size": db.bind.pool.size()
    }
