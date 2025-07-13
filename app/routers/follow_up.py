from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime

from .. import schemas, crud
from ..database import SessionLocal
from pathlib import Path

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


@router.post(
    "/follow-ups",
    response_model=schemas.FollowUp,
    status_code=status.HTTP_201_CREATED
)
async def create_follow_up(
    follow_up: schemas.FollowUpCreate,
    db: Session = Depends(get_db)
):
    """
    创建随访记录（移除前置验证，完全依赖crud层的自动创建）
    """
    try:
        return crud.create_follow_up(db=db, follow_up=follow_up)
    except HTTPException as e:
        # 保留原始HTTP异常
        raise
    except Exception as e:
        logger.error(f"创建随访记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器处理请求时发生错误: {str(e)}"
        )

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
    """生成可打印的HTML格式随访报告"""
    try:
        report_data = crud.get_follow_up_report_data(db, follow_up_id=follow_up_id)
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        report_data["report_date"] = datetime.now().strftime("%Y年%m月%d日")

        return templates.TemplateResponse(
            "reports/follow_up_report.html",
            {
                "request": request,
                "report": report_data,
                "now": current_time,
                "title": f"随访报告 #{follow_up_id}"
            }
        )
    except HTTPException:
        # 直接传递HTTP异常
        raise
    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )