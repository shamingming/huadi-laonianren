from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks

from app import models
from app.routers.follow_up import trigger_follow_up_scheduling
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
import os
from pathlib import Path
from app.crud import schedule_follow_up_automation
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
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
# 在main.py中添加（临时使用）


# 在 lifespan 中初始化调度器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    with engine.connect() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("elderly"):
            Base.metadata.create_all(bind=engine)

    # 初始化 APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # 添加测试任务（每分钟执行一次）
    scheduler.add_job(
        test_scheduled_task,
        CronTrigger(second="*/10"),  # 每10秒触发一次（测试用）
        id="test_task"
    )

    # 添加随访排期任务（每天上午9点执行）
    scheduler.add_job(
        schedule_follow_ups,
        CronTrigger(hour=9, minute=0),  # 每天9:00 AM
        id="follow_up_scheduler"
    )

    yield

    # 关闭时清理调度器
    scheduler.shutdown()

# 测试任务
def test_scheduled_task():
    print(f"定时任务测试: {datetime.now()}")

# 随访排期任务（需实现具体逻辑）
def schedule_follow_ups():
    with SessionLocal() as db:
        # 只处理自动排期的随访
        recurring_follows = db.query(models.FollowUp).filter(
            models.FollowUp.is_recurring == True,
            models.FollowUp.next_follow_up_date <= datetime.now()
        ).all()

        for follow in recurring_follows:
            new_follow = models.FollowUp(
                elderly_id=follow.elderly_id,
                doctor_id=follow.doctor_id,
                follow_up_date=follow.next_follow_up_date,
                next_follow_up_date=follow.next_follow_up_date + timedelta(days=follow.schedule_interval),
                # ...复制其他必要字段
            )
            db.add(new_follow)
        db.commit()

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

@app.get("/migrate")
def migrate_db():
    Base.metadata.drop_all(bind=engine)  # 删除旧表
    Base.metadata.create_all(bind=engine)  # 创建新表
    return {"message": "数据库表结构已更新"}
