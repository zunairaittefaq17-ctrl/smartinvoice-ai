from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class InvoiceItemSchema(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float

class InvoiceCreate(BaseModel):
    invoice_number: str
    date: date
    vendor: str
    items: List[InvoiceItemSchema]
    subtotal: float
    tax: float
    total: float
    currency: str = "USD"
    category: str

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    date: date
    vendor: str
    subtotal: float
    tax: float
    total: float
    currency: str
    category: str
    ai_confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_expenses: float
    monthly_expenses: float
    top_category: str
    top_vendor: str
    invoices_count: int

class AIInsight(BaseModel):
    summary: str
    savings_tips: str
    warnings: List[str]
