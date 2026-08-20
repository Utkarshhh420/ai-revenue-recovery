# AI Revenue Recovery Agent

**Track:** AI Revenue Recovery
**Built for:** Razorpay AI Buildathon

An AI-powered backend service that automatically tracks overdue invoices
and drafts escalating payment-reminder messages, so a finance/collections
team spends less time manually chasing payments and more time on
higher-value work.

## Problem it solves

Businesses lose time and revenue when overdue invoices are followed up
inconsistently — reminders are sent late, tone doesn't match how overdue
the payment is, and tracking who's been reminded (and how many times) is
manual. This agent automates that entire loop:

1. **Detects** which invoices have crossed their due date and are now overdue.
2. **Escalates tone automatically** based on how late the payment is:
   - `0–7 days overdue` → gentle, friendly nudge
   - `8–21 days overdue` → firm follow-up
   - `22+ days overdue` → final notice
3. **Generates the reminder message with AI** (Claude), personalized to
   the customer, invoice amount, and days overdue — with a rule-based
   template as an automatic fallback if no API key is configured, so the
   project always runs end-to-end.
4. **Tracks reminder history** per invoice and gives a dashboard summary
   of total outstanding and overdue amounts.

## Tech stack

- **FastAPI** — REST API backend
- **SQLAlchemy + SQLite** — data storage (zero setup required)
- **Pydantic** — request/response validation
- **Anthropic Claude API** (optional) — natural-language reminder generation

## Project structure

```
ai-revenue-recovery/
├── app/
│   ├── main.py        # FastAPI routes
│   ├── models.py      # Invoice DB model
│   ├── schemas.py      # Pydantic request/response schemas
│   ├── database.py     # DB session setup
│   └── ai_agent.py     # Escalation logic + AI/template reminder generation
├── seed_data.py         # Loads sample invoices for a quick demo
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & running locally

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd ai-revenue-recovery

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add your Anthropic API key for AI-generated messages
cp .env.example .env
# edit .env and paste your key — otherwise templates are used automatically

# 4. Seed sample data
python seed_data.py

# 5. Run the server
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive Swagger API docs.

## API endpoints

| Method | Endpoint                          | Description                                  |
|--------|------------------------------------|-----------------------------------------------|
| POST   | `/invoices`                        | Create a new invoice                          |
| GET    | `/invoices`                        | List all invoices                             |
| GET    | `/invoices/overdue`                | List only overdue invoices                    |
| POST   | `/invoices/{id}/mark-paid`         | Mark an invoice as paid                       |
| POST   | `/invoices/{id}/generate-reminder` | AI-generate a reminder for an overdue invoice |
| GET    | `/dashboard/summary`               | Outstanding/overdue totals and counts         |

### Example: generate a reminder

```bash
curl -X POST http://127.0.0.1:8000/invoices/1/generate-reminder
```

```json
{
  "invoice_number": "INV-1001",
  "escalation_level": "gentle",
  "days_overdue": 3,
  "message": "Hi Ravi Traders,\n\nThis is a friendly reminder that invoice INV-1001 for ₹45,000.00 was due on 2026-08-17...",
  "generated_by": "template"
}
```

## Future improvements

- Actually send reminders via email/SMS instead of just generating text
- Auto-schedule reminders on a cron job as invoices cross overdue thresholds
- Add a small analytics view showing average days-to-pay per customer
- Multi-currency support

## Author

Utkarsh Jaiswal — B.Tech CSE, NIET
