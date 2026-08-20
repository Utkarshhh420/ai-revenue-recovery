"""
Data models for the Revenue Recovery system.

Invoice: represents a bill raised to a customer.
Status lifecycle: PENDING -> PAID
                          -> OVERDUE (auto-detected when due_date has passed)
"""
from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, Enum
import enum
from .database import Base


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)
    reminders_sent = Column(Integer, default=0)

    def days_overdue(self) -> int:
        delta = date.today() - self.due_date
        return max(delta.days, 0)
