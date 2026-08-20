"""
Seeds the database with sample invoices (some overdue, some pending)
so the API and reminder agent can be demoed immediately.

Run: python seed_data.py
"""
from datetime import date, timedelta
from app.database import engine, SessionLocal
from app import models

models.Base.metadata.create_all(bind=engine)

sample_invoices = [
    {
        "customer_name": "Ravi Traders",
        "customer_email": "ravi.traders@example.com",
        "amount": 45000,
        "invoice_number": "INV-1001",
        "due_date": date.today() - timedelta(days=3),
    },
    {
        "customer_name": "Sunrise Textiles",
        "customer_email": "accounts@sunrisetextiles.example.com",
        "amount": 128000,
        "invoice_number": "INV-1002",
        "due_date": date.today() - timedelta(days=15),
    },
    {
        "customer_name": "Nova Electronics",
        "customer_email": "billing@novaelectronics.example.com",
        "amount": 76500,
        "invoice_number": "INV-1003",
        "due_date": date.today() - timedelta(days=30),
    },
    {
        "customer_name": "Green Valley Foods",
        "customer_email": "finance@greenvalley.example.com",
        "amount": 32000,
        "invoice_number": "INV-1004",
        "due_date": date.today() + timedelta(days=5),  # not due yet
    },
]

db = SessionLocal()
for data in sample_invoices:
    existing = db.query(models.Invoice).filter(
        models.Invoice.invoice_number == data["invoice_number"]
    ).first()
    if not existing:
        db.add(models.Invoice(**data))
db.commit()
db.close()

print(f"Seeded {len(sample_invoices)} sample invoices into revenue_recovery.db")
