from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime,timezone
from pydantic import BaseModel, validator

from .. import schemas, crud
from ..crud import schedule_follow_up_automation
from ..database import SessionLocal
from pathlib import Path

from ..models import FollowUp

# 在 follow_up.py 中修改
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

import os
print(f"模板目录绝对路径: {template_dir}")
print(f"模板文件是否存在: {(template_dir / 'reports' / 'follow_up_report.html').exists()}")
router = APIRouter(
    prefix="",
    tags=["随访管理"],
    responses={
        404: {"description": "资源不存在"},
        422: {"description": "参数验证错误"},
        500: {"description": "服务器内部错误"}
    }
)

logger = logging.getLogger(__name__)
# templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        # 不捕获HTTP异常
        raise
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        db.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库连接失败"
        )
    finally:
        db.close()

class FollowUpCreate(BaseModel):
    elderly_id: int
    doctor_id: int
    follow_up_date: str  # 使用字符串格式接收
    content: str = ""
    result: str = ""

    @validator('follow_up_date')
    def validate_date(cls, v):
        # 如果已经是datetime对象，直接返回
        if isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            raise ValueError("日期格式应为 YYYY-MM-DD HH:mm:ss")

@router.post("/follow-ups")
async def create_follow_up(
    follow_up: schemas.FollowUpCreate,
    db: Session = Depends(get_db)
):
    try:
        # 确保follow_up_date是datetime对象
        if isinstance(follow_up.follow_up_date, str):
            follow_up.follow_up_date = datetime.strptime(follow_up.follow_up_date, "%Y-%m-%d %H:%M:%S")

        return crud.create_follow_up(db, follow_up)
    except Exception as e:
        logger.error(f"创建随访记录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
@router.get(
    "/follow-ups",
    response_model=List[schemas.FollowUp],
    summary="获取随访记录列表",
    description="支持分页查询的随访记录列表",
    responses={
        200: {"description": "成功获取分页数据"}
    }
)
async def read_follow_ups(
        skip: int = 0,
        limit: int = 100,
        elderly_id: int = None,
        doctor_id: int = None,
        db: Session = Depends(get_db)
):
    """获取随访记录列表"""
    try:
        return crud.get_follow_ups(
            db,
            skip=skip,
            limit=min(limit, 1000),
            elderly_id=elderly_id,
            doctor_id=doctor_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取随访记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据时发生错误"
        )

@router.get(
    "/follow-ups/{follow_up_id}/report",
    summary="生成随访报告",
    description="生成包含详细信息的HTML报告",
    responses={
        200: {"content": {"text/html": {}}},
        404: {"description": "记录不存在"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_follow_up_report(
        request: Request,
        follow_up_id: int,
        db: Session = Depends(get_db)
):
    try:
        logger.info(f"请求报告 - ID: {follow_up_id}")
        report_data = crud.get_follow_up_report_data(db, follow_up_id=follow_up_id)

        if not report_data:
            logger.error(f"报告数据为空 - ID: {follow_up_id}")
            raise HTTPException(status_code=404, detail="报告数据为空")

        logger.debug(f"报告数据: {report_data}")
        return templates.TemplateResponse(
            "reports/follow_up_report.html",
            {
                "request": request,
                "report": report_data,
                "now": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
                "title": f"随访报告 #{follow_up_id}"
            }
        )
    except Exception as e:
        logger.error(f"报告生成失败 - ID: {follow_up_id} - 错误: {str(e)}", exc_info=True)
        raise



# 在follow_up.py中添加以下路由

# 患者管理路由
@router.post(
    "/elderly",
    response_model=schemas.Elderly,
    status_code=status.HTTP_201_CREATED,
    summary="创建老人信息",
    description="添加一个新的老人信息"
)
async def create_elderly(
    elderly: schemas.ElderlyCreate,
    db: Session = Depends(get_db)
):
    return crud.create_elderly(db=db, elderly=elderly)

@router.delete(
    "/elderly/{elderly_id}",
    status_code=status.HTTP_200_OK,
    summary="删除老人信息",
    description="根据ID删除老人信息"
)
async def delete_elderly(
    elderly_id: int,
    db: Session = Depends(get_db)
):
    return crud.delete_elderly(db=db, elderly_id=elderly_id)

# 医生管理路由
@router.post(
    "/doctors",
    response_model=schemas.Doctor,
    status_code=status.HTTP_201_CREATED,
    summary="创建医生信息",
    description="添加一个新的医生信息"
)
async def create_doctor(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db)
):
    return crud.create_doctor(db=db, doctor=doctor)

@router.delete(
    "/doctors/{doctor_id}",
    status_code=status.HTTP_200_OK,
    summary="删除医生信息",
    description="根据ID删除医生信息"
)
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    return crud.delete_doctor(db=db, doctor_id=doctor_id)

@router.get(
    "/elderly",
    response_model=List[schemas.Elderly],
    summary="获取老人列表",
    description="获取所有老人信息列表"
)
async def read_elderlies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_elderlies(db, skip=skip, limit=limit)

@router.get(
    "/doctors",
    response_model=List[schemas.Doctor],
    summary="获取医生列表",
    description="获取所有医生信息列表"
)
async def read_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_doctors(db, skip=skip, limit=limit)

@router.delete(
    "/follow-ups/{follow_up_id}",
    status_code=status.HTTP_200_OK,
    summary="删除随访记录",
    description="根据ID删除随访记录"
)
async def delete_follow_up(
    follow_up_id: int,
    db: Session = Depends(get_db)
):
    """删除随访记录"""
    try:
        return crud.delete_follow_up(db, follow_up_id=follow_up_id)
    except Exception as e:
        logger.error(f"删除随访记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除随访记录失败"
        )


@router.post(
    "/follow-ups/schedule",
    summary="手动触发随访排期",
    description="立即执行自动化随访排期任务（通常由系统定时调用）",
    status_code=202
)
async def trigger_follow_up_scheduling(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """供外部调用的排期接口"""
    background_tasks.add_task(schedule_follow_up_automation, db)
    return {"message": "随访排期任务已提交后台执行"}