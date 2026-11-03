from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    customer_email = Column(String)
    status = Column(String, default="Open")  # Open, Pending, Closed
    created_at = Column(DateTime, default=datetime.utcnow)

    # العلاقة مع جدول تحليلات الذكاء الاصطناعي
    ai_analysis = relationship("AILog", back_populates="ticket", uselist=False)

class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    sentiment = Column(String)       # Urgent, Frustrated, Neutral, Positive
    category = Column(String)        # Technical, Billing, Sales, General
    suggested_reply = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # الربط العكسي مع التذكرة
    ticket = relationship("Ticket", back_populates="ai_analysis")