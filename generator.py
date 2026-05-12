import os
import random
from groq import Groq

# التأكد من الساروت
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate():
    title = f"نظام غذائي رياضي 2026 - وزن {random.randint(60,100)} كجم"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO عن {title}"}],
            # هذا هو الموديل الجديد المعتمد حالياً
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content
        filename = f"post-{random.randint(1000,9999)}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"<html><body dir='rtl'><h1>{title}</h1>{body}</body></html>")
        print(f"✅ Success: {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate()
