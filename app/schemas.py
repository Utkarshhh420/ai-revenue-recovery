from datetime import date
from pydantic import BaseModel, EmailStr
from .models import InvoiceStatus


class InvoiceCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    amount: float
    invoice_number: str
    due_date: date


class InvoiceOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    amount: float
    invoice_number: str
    due_date: date
    status: InvoiceStatus
    reminders_sent: int

    class Config:
        from_attributes = True
