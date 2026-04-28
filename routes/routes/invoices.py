from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from database import get_db
from models import Invoice
from schemas import InvoiceResponse
from services.ai_processor import process_invoice_image
from auth import get_current_user
from models import User

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/", response_model=InvoiceResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith('image/') and not file.content_type == 'application/pdf':
        raise HTTPException(status_code=400, detail="Only images and PDFs supported")
    
    image_bytes = await file.read()
    invoice = await process_invoice_image(image_bytes, current_user.id, db)
    return invoice

@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).filter(Invoice.owner_id == current_user.id).order_by(Invoice.created_at.desc()).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, 
        Invoice.owner_id == current_user.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
