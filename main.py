"""
AI Revenue Recovery Agent
==========================
A small backend service that tracks invoices, automatically detects
overdue payments, and uses an AI agent to draft escalating payment
reminder messages — reducing manual follow-up work for a finance/
collections team.

Run with:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs for interactive API docs.
"""
from datetime import date
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from .ai_agent import generate_reminder

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Revenue Recovery Agent",
    description="Tracks overdue invoices and generates AI-drafted payment reminders.",
    version="1.0.0",
)


def _sync_overdue_status(db: Session):
    """Flip any PENDING invoice past its due date to OVERDUE."""
    pending = db.query(models.Invoice).filter(
        models.Invoice.status == models.InvoiceStatus.PENDING
    ).all()
    for inv in pending:
        if inv.due_date < date.today():
            inv.status = models.InvoiceStatus.OVERDUE
    db.commit()


@app.post("/invoices", response_model=schemas.InvoiceOut)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    """Add a new invoice to the system."""
    existing = db.query(models.Invoice).filter(
        models.Invoice.invoice_number == invoice.invoice_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invoice number already exists")

    db_invoice = models.Invoice(**invoice.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@app.get("/invoices", response_model=List[schemas.InvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    """List every invoice, auto-refreshing overdue status first."""
    _sync_overdue_status(db)
    return db.query(models.Invoice).all()


@app.get("/invoices/overdue", response_model=List[schemas.InvoiceOut])
def list_overdue_invoices(db: Session = Depends(get_db)):
    """List only invoices that are currently overdue."""
    _sync_overdue_status(db)
    return db.query(models.Invoice).filter(
        models.Invoice.status == models.InvoiceStatus.OVERDUE
    ).all()


@app.post("/invoices/{invoice_id}/mark-paid", response_model=schemas.InvoiceOut)
def mark_paid(invoice_id: int, db: Session = Depends(get_db)):
    """Mark an invoice as paid (stops further reminders)."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = models.InvoiceStatus.PAID
    db.commit()
    db.refresh(invoice)
    return invoice


@app.post("/invoices/{invoice_id}/generate-reminder")
def generate_invoice_reminder(invoice_id: int, db: Session = Depends(get_db)):
    """
    Core AI feature: generate an escalating reminder message for one
    overdue invoice, and increment its reminder counter.
    """
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status != models.InvoiceStatus.OVERDUE:
        raise HTTPException(status_code=400, detail="Invoice is not overdue")

    result = generate_reminder(invoice)
    invoice.reminders_sent += 1
    db.commit()

    return result


@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Quick stats: total outstanding amount, count by status."""
    _sync_overdue_status(db)
    invoices = db.query(models.Invoice).all()

    total_outstanding = sum(
        inv.amount for inv in invoices if inv.status != models.InvoiceStatus.PAID
    )
    overdue_amount = sum(
        inv.amount for inv in invoices if inv.status == models.InvoiceStatus.OVERDUE
    )

    return {
        "total_invoices": len(invoices),
        "pending": sum(1 for i in invoices if i.status == models.InvoiceStatus.PENDING),
        "overdue": sum(1 for i in invoices if i.status == models.InvoiceStatus.OVERDUE),
        "paid": sum(1 for i in invoices if i.status == models.InvoiceStatus.PAID),
        "total_outstanding_amount": round(total_outstanding, 2),
        "overdue_amount": round(overdue_amount, 2),
    }


@app.get("/")
def root():
    return {"message": "AI Revenue Recovery Agent is running. Visit /docs for API documentation."}
