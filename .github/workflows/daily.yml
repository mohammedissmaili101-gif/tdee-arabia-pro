import os
import random
from groq import Groq

# إعداد العميل - تأكد من وجود GROQ_API_KEY في GitHub Secrets
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate():
    # اختيار وزن عشوائي للعنوان
    weight = random.randint(60, 100)
    title = f"نظام غذائي رياضي لعام 2026 - وزن {weight} كجم"
    
    try:
        # طلب المقال من Groq باستخدام الموديل الجديد والفعال
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}"}],
            model="llama-3.3-70b-versatile",
        )
        
        body = res.choices[0].message.content
        
        # إنشاء اسم ملف فريد
        filename = f"post-{random.randint(1000, 9999)}.html"
        
        # كتابة الملف بتنسيق HTML بسيط
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>{title}</title></head>
            <body style="font-family: Arial; padding: 40px; line-height: 1.6;">
                <h1>{title}</h1>
                <div>{body.replace('\\n', '<br>')}</div>
            </body>
            </html>
            """)
            
        print(f"✅ تم بنجاح: {filename}")
        
    except Exception as e:
        print(f"❌ خطأ تقني: {e}")

if __name__ == "__main__":
    generate()
