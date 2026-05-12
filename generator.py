import os
import random
import datetime
import re
import requests
from groq import Groq

# 1. الإعدادات والربط
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia.vercel.app"
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

# ألوان احترافية للفقرات
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

def get_gym_image(category):
    keywords = {
        "تنشيف": "fitness,abs,cardio",
        "تضخيم": "bodybuilding,gym,muscle",
        "مكملات": "protein,supplements",
        "تغذية": "healthy-food,diet",
        "تمارين": "workout,training"
    }
    kw = keywords.get(category, "fitness")
    rand = random.randint(1, 50000)
    return f"https://loremflickr.com/1200/800/{kw}/all?lock={rand}"

def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(sitemap_file):
        content = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url><url><loc>{DOMAIN}/blog.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url><url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url></urlset>'
        with open(sitemap_file, "w", encoding="utf-8") as f: f.write(content)
    else:
        with open(sitemap_file, "r", encoding="utf-8") as f: content = f.read()
        if url not in content:
            updated = content.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>\n</urlset>")
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
        elif p.startswith('* '):
            item = p.replace('* ', '')
            formatted_html += f'<div class="flex items-center gap-3 mb-4 p-5 bg-white rounded-2xl border border-slate-100 shadow-sm text-right"><span class="bg-blue-600 text-white p-2 rounded-lg text-xs">⚡</span><p class="font-bold text-slate-700">{item}</p></div>'
        else:
            style = random.choice(paragraph_styles)
            formatted_html += f'<div class="p-8 rounded-[2.5rem] border {style} shadow-sm leading-[2.6rem] text-xl mb-8 text-right font-medium">{p}</div>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # السطر 82: الماركر دابا عامر ومضمون
    marker = ''
    
    new_card = f"""
    <div class="blog-card bg-white rounded-[3rem] shadow-xl overflow-hidden hover:scale-[1.02] transition-all duration-500 border border-slate-100 group" data-category="{category}">
        <div class="relative h-72">
            <img src="{image_url}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" alt="{title}">
            <div class="absolute top-6 right-6 bg-blue-600 text-white text-xs font-bold px-5 py-2 rounded-full shadow-2xl">{category}</div>
        </div>
        <div class="p-10 text-right">
            <span class="text-blue-500 font-bold text-sm tracking-widest">{today}</span>
            <h3 class="post-title text-2xl font-black mt-4 mb-8 text-slate-900 leading-snug h-24 overflow-hidden">{title}</h3>
            <a href="./{file_slug}" class="inline-block w-full text-center bg-slate-900 text-white font-black py-5 rounded-2xl hover:bg-blue-600 transition-all shadow-xl">إقرأ التفاصيل ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>مدونة TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50 text-slate-900">
            <nav class="bg-white p-6 shadow-sm sticky top-0 z-50 text-right"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="font-bold text-slate-600">الرئيسية</a></div></nav>
            <main class="max-w-7xl mx-auto px-6 py-16">
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
            # ترميم الطوارئ: يلا مالقاش الماركر كيحطو تحت الـ blog-grid
            grid_tag = 'id="blog-grid">'
            if grid_tag in content:
                updated = content.replace(grid_tag, f'{grid_tag}\n{marker}\n{new_card}')
                with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    topics = {
        "تنشيف": ["أسرار حرق الدهون", "كيف تنشف بسرعة", "تمارين البطن"],
        "تضخيم": ["دليل تضخيم العضلات", "برنامج الضخامة العضلية", "سر الوجبات الضخمة"],
        "تغذية": ["وجبات بروتينية رخيصة", "حساب السعرات بدقة", "أفضل مصادر الكارب"],
        "مكملات": ["فوائد الكرياتين", "مراجعة الواي بروتين", "مكملات الطاقة"],
        "تمارين": ["أخطاء البنش برس", "فوائد السكوات", "تمارين منزلية"]
    }
    cat_key = random.choice(list(topics.keys()))
    topic = random.choice(topics[cat_key])
    title = f"{topic} - دليل 2026"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي بالعربية عن {title}. استعمل عناوين فرعية ونقاط."}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(100000, 999999)}.html"
        img = get_gym_image(cat_key)
        
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo';}}</style></head>
        <body class="bg-slate-50">
            <nav class="bg-white p-6 shadow-sm sticky top-0 z-50 text-right"><div class="max-w-5xl mx-auto flex justify-between items-center"><a href="./blog.html" class="text-blue-600 font-bold">← رجوع</a><span class="font-black text-2xl">TDEE ARABIA 🔥</span></div></nav>
            <main class="max-w-5xl mx-auto my-12 px-6 text-right">
                <div class="relative h-[450px] rounded-[3rem] overflow-hidden shadow-2xl mb-[-80px] z-10 border-8 border-white"><img src="{img}" class="w-full h-full object-cover"><div class="absolute inset-0 bg-black/40 flex items-end p-12"><h1 class="text-white text-4xl font-black">{title}</h1></div></div>
                <article class="bg-white pt-32 pb-16 px-10 rounded-[4rem] shadow-xl relative z-0">{body}</article>
            </main></body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat_key)
        update_sitemap(slug)
        trigger_vercel_deploy()
        print(f"✅ Success: {slug}")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
