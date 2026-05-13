import os
import random
import datetime
import re
import requests
from groq import Groq

# الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def get_pexels_image(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}+fitness&per_page=1"
    try:
        r = requests.get(url, headers=headers)
        return r.json()['photos'][0]['src']['large2x']
    except:
        return "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg"

def format_content(text):
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            formatted += f'<h2 class="text-2xl font-bold text-blue-600 mt-8 mb-4">{p.replace("**","")}</h2>'
        else:
            formatted += f'<p class="text-lg text-slate-700 mb-6 leading-relaxed text-right">{p}</p>'
    return formatted

def update_blog(slug, title, img, cat):
    blog_file = "blog.html"
    marker = 'HERE_IS_THE_LIST_MARKER'
    card = f'''
    <div class="blog-card bg-white p-4 rounded-3xl shadow-sm border mb-6" data-title="{title}">
        <img src="{img}" class="w-full h-48 object-cover rounded-2xl mb-4">
        <span class="text-blue-600 font-bold text-sm">{cat}</span>
        <h3 class="text-xl font-black my-2">{title}</h3>
        <a href="./{slug}" class="text-blue-600 font-bold underline">إقرأ المزيد ←</a>
    </div>'''
    if os.path.exists(blog_file):
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(content.replace(marker, f"{marker}\n{card}"))

def generate_post():
    topics = {"تغذية": "بروتين طبيعي", "تدريب": "عضلات الصدر", "عقلية": "الاستمرار فالتمرين"}
    cat = random.choice(list(topics.keys()))
    title = f"دليل {topics[cat]} للمحترفين {random.randint(2025, 2026)}"
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال رياضي احترافي عن {title} بالعربية."}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(res.choices[0].message.content)
        img = get_pexels_image(topics[cat])
        slug = f"post-{random.randint(1000, 9999)}.html"
        
        html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-50 p-6"><article class="max-w-2xl mx-auto bg-white p-8 rounded-3xl shadow-lg"><img src="{img}" class="w-full rounded-2xl mb-8"><h1>{title}</h1>{body}</article></body></html>'''
        
        with open(slug, "w", encoding="utf-8") as f: f.write(html)
        update_blog(slug, title, img, cat)
        print(f"Done: {slug}")
    except Exception as e: print(e)

if __name__ == "__main__":
    generate_post()
