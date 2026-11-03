from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# مخطط عرض بيانات سجل الذكاء الاصطناعي
class AILogResponse(BaseModel):
    sentiment: str
    category: str
    suggested_reply: str

    class Config:
        from_attributes = True

# مخطط عرض التذكرة شاملة تحليل الذكاء الاصطناعي
class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    customer_email: str
    status: str
    created_at: datetime
    ai_analysis: Optional[AILogResponse] = None

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    title: str
    description: str
    customer_email: str