import os
import random
from groq import Groq

# غيخدم بـ الـ Key اللي غتحط فـ GitHub Secrets
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

weights = [70, 80, 90, 100]
goals = ["تنشيف", "تضخيم"]

def make_post():
    w, g = random.choice(weights), random.choice(goals)
    prompt = f"اكتب مقال SEO مطول بالعربية عن {g} لوزن {w}kg. استعمل لغة قوية."
    
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    # تصنيع صفحة HTML للمقال
    content = chat.choices[0].message.content
    with open(f"article-{w}-{random.randint(1,999)}.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body style='font-family:sans-serif; padding:40px;'>{content}</body></html>")

if __name__ == "__main__":
    make_post()
