from sqlalchemy.orm import Session
from models import Invoice, InvoiceItem, User
from schemas import InvoiceCreate
from services.groq_client import extract_invoice_data
from services.ocr import extract_text_from_image
import base64
from datetime import datetime
from typing import List, Dict, Any

async def process_invoice_image(image_bytes: bytes, user_id: int, db: Session) -> Invoice:
    """Complete AI invoice processing pipeline"""
    
    # Step 1: OCR Text Extraction
    raw_text = extract_text_from_image(image_bytes)
    
    # Step 2: AI Structured Extraction
    invoice_data = await extract_invoice_data(raw_text)
    
    # Step 3: Validate and create structured data
    if not invoice_data or not invoice_data.get('total'):
        raise ValueError("Could not extract invoice data")
    
    # Parse date
    try:
        invoice_date = datetime.strptime(invoice_data['date'], '%Y-%m-%d').date()
    except:
        invoice_date = datetime.now().date()
    
    # Create invoice
    db_invoice = Invoice(
        invoice_number=invoice_data.get('invoice_number', 'N/A'),
        date=invoice_date,
        vendor=invoice_data.get('vendor', 'Unknown'),
        subtotal=invoice_data.get('subtotal', 0.0),
        tax=invoice_data.get('tax', 0.0),
        total=invoice_data.get('total', 0.0),
        currency=invoice_data.get('currency', 'USD'),
        category=invoice_data.get('category', 'General'),
        raw_text=raw_text,
        ai_confidence=0.85,  # Mock confidence
        owner_id=user_id
    )
    
    # Add items
    for item in invoice_data.get('items', []):
        db_item = InvoiceItem(
            description=item.get('description', ''),
            quantity=item.get('quantity', 0),
            unit_price=item.get('unit_price', 0),
            total_price=item.get('total_price', 0),
            invoice=db_invoice
        )
        db_invoice.items.append(db_item)
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice
