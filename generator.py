import os
import random
import datetime
import re
import requests
from groq import Groq

# 1. الإعدادات (تأكد من الرابط الصحيح لـ Vercel هنا)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app" 
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

paragraph_styles = [
    "bg-white border-r-4 border-blue-500 text-slate-800",
    "bg-blue-50 border-r-4 border-indigo-400 text-indigo-900",
    "bg-slate-50 border-r-4 border-slate-400 text-slate-900",
    "bg-emerald-50 border-r-4 border-emerald-400 text-emerald-900"
]

def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK)
            print("🚀 Vercel Deployment Started!")
        except Exception as e: print(f"⚠️ Deployment Hook Error: {e}")

def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(sitemap_file):
        content = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod></url></urlset>'
        with open(sitemap_file, "w", encoding="utf-8") as f: f.write(content)
    
    with open(sitemap_file, "r", encoding="utf-8") as f: content = f.read()
    if url not in content:
        updated = content.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>\n</urlset>")
        with open(sitemap_file, "w", encoding="utf-8") as f: f.write(updated)

def format_content(text):
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-3xl font-black text-slate-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-slate-100 py-4 rounded-l-2xl shadow-sm text-right">{title}</h2>'
        else:
            style = random.choice(paragraph_styles)
            formatted_html += f'<div class="p-8 rounded-[2.5rem] border {style} shadow-sm leading-[2.6rem] text-xl mb-8 font-medium text-right">{p}</div>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    # ماركر نصي مستحيل يتمسح
    marker = 'HERE_IS_THE_LIST_MARKER'
    
    new_card = f"""
    <div class="blog-card bg-white rounded-[3rem] shadow-xl overflow-hidden mb-10 border border-slate-100">
        <img src="{image_url}" class="w-full h-72 object-cover">
        <div class="p-10 text-right">
            <span class="text-blue-500 font-bold">{today}</span>
            <h3 class="post-title text-2xl font-black mt-4 mb-8 text-slate-900">{title}</h3>
            <a href="./{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-black py-5 rounded-2xl hover:bg-slate-900 transition-all shadow-lg">إقرأ التفاصيل ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>TDEE Arabia Blog</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50">
            <nav class="bg-white p-6 shadow-sm border-b"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</h1></div></nav>
            <main class="max-w-7xl mx-auto px-6 py-16 text-right">
                <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                    {marker}
                    {new_card}
                </div>
            </main>
        </body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)
        else:
            updated = content.replace('id="blog-grid">', f'id="blog-grid">\n{marker}\n{new_card}')
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    topics = {"تنشيف": "أسرار حرق الدهون", "تضخيم": "أقوى نظام تضخيم", "تغذية": "وجبات اقتصادية"}
    cat = random.choice(list(topics.keys()))
    title = topics[cat] + " 2026"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي مطول بالعربية عن {title}"}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = f"https://loremflickr.com/1200/800/gym/all?lock={random.randint(1,999)}"
        
        # إنشاء المقال بتنسيق Tailwind (باش ما يبقاش 404 أو صفحة بيضاء)
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50 text-right">
            <main class="max-w-4xl mx-auto py-20 px-6">
                <a href="./blog.html" class="text-blue-600 font-bold mb-10 inline-block">← العودة للمدونة</a>
                <img src="{img}" class="w-full rounded-[3rem] shadow-2xl mb-12">
                <h1 class="text-5xl font-black mb-10 text-slate-900">{title}</h1>
                <article>{body}</article>
            </main>
        </body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        trigger_vercel_deploy()
        print(f"✅ تم بنجاح: {slug}")
        
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
