from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db
from ai_service import analyze_ticket_with_ai

# إنشاء الجداول تلقائياً
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart CRM AI Backend")

# إعدادات CORS للاتصال بالواجهة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Smart CRM API Running"}

# 1. إضافة تذكرة جديدة وتحليلها بالذكاء الاصطناعي
@app.post("/tickets/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        customer_email=ticket.customer_email
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    # تحليل الذكاء الاصطناعي
    ai_result = analyze_ticket_with_ai(ticket.title, ticket.description)

    db_ai_log = models.AILog(
        ticket_id=db_ticket.id,
        sentiment=ai_result.get("sentiment", "محايد"),
        category=ai_result.get("category", "دعم عام"),
        suggested_reply=ai_result.get("suggested_reply", "")
    )
    db.add(db_ai_log)
    db.commit()

    db.refresh(db_ticket)
    return db_ticket

# 2. عرض جميع التذاكر
@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

# 3. تحديث حالة التذكرة (إغلاقها)
@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket

# 4. [جديد] API الإحصائيات ومؤشرات الأداء
@app.get("/tickets/stats")
def get_ticket_stats(db: Session = Depends(get_db)):
    total_tickets = db.query(models.Ticket).count()
    open_tickets = db.query(models.Ticket).filter(models.Ticket.status == "Open").count()
    closed_tickets = db.query(models.Ticket).filter(models.Ticket.status == "Closed").count()
    
    # حساب الحالات العاجلة والغاضبة
    urgent_tickets = db.query(models.AILog).filter(models.AILog.sentiment.like("%عاجل%")).count()
    
    return {
        "total": total_tickets,
        "open": open_tickets,
        "closed": closed_tickets,
        "urgent": urgent_tickets
    }