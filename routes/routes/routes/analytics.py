from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models import Invoice, User
from schemas import AnalyticsSummary
from services.groq_client import generate_insights
from auth import get_current_user
from typing import Dict, Any
import json

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=Dict)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Monthly summary
    now = func.now()
    monthly_query = db.query(
        func.sum(Invoice.total).label('monthly_expenses'),
        func.count(Invoice.id).label('invoices_count'),
        func.max(Invoice.vendor).label('top_vendor')
    ).filter(
        Invoice.owner_id == current_user.id,
        extract('year', Invoice.date) == extract('year', now),
        extract('month', Invoice.date) == extract('month', now)
    ).first()
    
    # Total expenses
    total_expenses = db.query(func.sum(Invoice.total)).filter(Invoice.owner_id == current_user.id).scalar() or 0
    
    # Top category
    top_category = db.query(Invoice.category, func.sum(Invoice.total)) \
        .filter(Invoice.owner_id == current_user.id) \
        .group_by(Invoice.category) \
        .order_by(func.sum(Invoice.total).desc()) \
        .first()
    
    summary = AnalyticsSummary(
        total_expenses=total_expenses,
        monthly_expenses=monthly_query.monthly_expenses or 0,
        top_category=top_category[0] if top_category else "N/A",
        top_vendor=monthly_query.top_vendor or "N/A",
        invoices_count=monthly_query.invoices_count or 0
    )
    
    # Generate AI insights
    insights = await generate_insights({
        'total_expenses': summary.total_expenses,
        'monthly_expenses': summary.monthly_expenses,
        'top_category': summary.top_category,
        'top_vendor': summary.top_vendor
    })
    
    return {
        "summary": summary.dict(),
        "insights": insights
    }

@router.get("/monthly")
async def get_monthly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Monthly breakdown for charts
    monthly_data = db.query(
        extract('year', Invoice.date).label('year'),
        extract('month', Invoice.date).label('month'),
        func.sum(Invoice.total).label('total')
    ).filter(Invoice.owner_id == current_user.id) \
     .group_by(extract('year', Invoice.date), extract('month', Invoice.date)) \
     .order_by(extract('year', Invoice.date), extract('month', Invoice.date)) \
     .all()
    
    return [{"month": f"{m.year}-{m.month:02d}", "total": float(m.total)} for m in monthly_data]
