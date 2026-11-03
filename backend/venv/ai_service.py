import os
import json
import re
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# تحديد المسار المطلق لملف .env داخل مجلد backend
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def analyze_ticket_with_ai(title: str, description: str):
    prompt = f"""
    You are an automated CRM assistant. Analyze the following support ticket and produce ONLY valid JSON.

    Ticket Title: {title}
    Ticket Description: {description}

    Return a JSON object containing EXACTLY these keys:
    1. "sentiment": One of ["عاجل / غاضب", "محايد", "إيجابي"]
    2. "category": One of ["فواتير ودفع", "دعم فني", "مبيعات", "دعم عام"]
    3. "suggested_reply": A professional response in Arabic addressing the user's issue in 2 sentences.

    Example Format:
    {{"sentiment": "عاجل / غاضب", "category": "فواتير ودفع", "suggested_reply": "نعتذر عن المشكلة، سنقوم بمراجعة العملية وإعادة المبلغ لحسابكم في أقرب وقت."}}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON generator. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )

        raw_content = response.choices[0].message.content.strip()
        
        # استخراج كائن الـ JSON بأمان باستخدام التعبيرات النمطية (Regex)
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        
        # إذا لم يتم العثور على أقواس JSON، يتم تحويل النص يدوياً
        return json.loads(raw_content)

    except Exception as e:
        print(f"\n================ GROQ ERROR LOG ================\n{e}\n================================================\n")
        
        # تحليل احتياطي ذكي بناءً على الكلمات المفتاحية في حال حدوث أي خطأ في الاتصال
        text = f"{title} {description}".lower()
        
        category = "دعم عام"
        sentiment = "محايد"
        
        if any(word in text for word in ["دفع", "فلوس", "بطاقة", "استرجاع", "مبلغ", "فاتورة", "خصم"]):
            category = "فواتير ودفع"
            sentiment = "عاجل / غاضب"
            reply = f"أهلاً بك، تم استلام تذكرتك بخصوص '{title}'. أعدنا توجيه الطلب لقسم الفواتير والمالية للتحقق من العملية وإعادة المبلغ لك فوراً."
        elif any(word in text for word in ["بطيء", "انترنت", "خطأ", "عطل", "لا يعمل", "سيرفر", "مشكلة"]):
            category = "دعم فني"
            sentiment = "عاجل / غاضب"
            reply = f"أهلاً بك، نعتذر عن خلل '{title}'. تم إرسال البلاغ لفريق الدعم الفني لمتابعة المشكلة وإصلاحها."
        else:
            reply = f"أهلاً بك، تم استلام تذكرتك بخصوص '{title}' وسيقوم فريق الدعم بالرد عليك في أقرب وقت."

        return {
            "sentiment": sentiment,
            "category": category,
            "suggested_reply": reply
        }