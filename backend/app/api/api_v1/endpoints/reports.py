from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import structlog

from app.db.database import get_db
from app.models.models import Report
from app.schemas.report import ReportCreate, ReportResponse

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ReportResponse])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all reports"""
    try:
        reports = db.query(Report).filter(Report.is_active == True).offset(skip).limit(limit).all()
        return reports
    except Exception as e:
        logger.error("Failed to fetch reports", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch reports")


@router.post("/", response_model=ReportResponse)
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new report"""
    try:
        db_report = Report(**report.dict())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        logger.info("Report created", report_id=db_report.id, report_name=db_report.name)
        return db_report
    except Exception as e:
        logger.error("Failed to create report", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create report")


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report"""
    try:
        report = db.query(Report).filter(Report.id == report_id, Report.is_active == True).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch report", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch report")