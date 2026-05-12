import os
import random
import datetime
import re
import requests
from groq import Groq

# 1. الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia.vercel.app"
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

paragraph_styles = [
    "bg-white border-r-4 border-blue-500 text-slate-800",
    "bg-blue-50 border-r-4 border-indigo-400 text-indigo-900",
    "bg-slate-50 border-r-4 border-slate-400 text-slate-900"
]

def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK)
            print("🚀 Vercel Deployment Triggered!")
        except Exception as e: print(f"⚠️ Hook Error: {e}")

def get_gym_image(category):
    keywords = {"تنشيف": "fitness", "تضخيم": "bodybuilding", "تغذية": "healthy-food", "مكملات": "supplements", "تمارين": "workout"}
    kw = keywords.get(category, "fitness")
    return f"https://loremflickr.com/1200/800/{kw}/all?lock={random.randint(1, 9999)}"

def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(sitemap_file):
        content = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod></url></urlset>'
        with open(sitemap_file, "w") as f: f.write(content)
    
    with open(sitemap_file, "r") as f: content = f.read()
    if url not in content:
        updated = content.replace("</urlset>", f"<url><loc>{url}</loc><lastmod>{today}</lastmod></url></urlset>")
        with open(sitemap_file, "w") as f: f.write(updated)

def format_content(text):
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?]', '', text)
    paragraphs = text.split('\n')
    html = ""
    for p in paragraphs:
        if not p.strip(): continue
        style = random.choice(paragraph_styles)
        html += f'<div class="p-6 rounded-2xl mb-4 {style}">{p.strip()}</div>'
    return html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    # الماركر هنا عامر ومصحح
    marker = ""
    new_card = f"""
    <div class="blog-card bg-white rounded-3xl shadow-lg overflow-hidden" data-category="{category}">
        <img src="{image_url}" class="w-full h-48 object-cover">
        <div class="p-6 text-right">
            <h3 class="text-xl font-bold mb-4">{title}</h3>
            <a href="./{file_slug}" class="text-blue-600 font-bold">إقرأ المزيد ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        # إنشاء ملف جديد في حالة عدم وجوده
        with open(blog_file, "w") as f:
            f.write(f'<html><body id="blog-grid">{marker}</body></html>')

    with open(blog_file, "r") as f: content = f.read()
    
    if marker in content:
        updated = content.replace(marker, f"{marker}\n{new_card}")
    else:
        # حل الطوارئ: يلا مالقاش الماركر كيحطو في أول الـ grid
        updated = content.replace('id="blog-grid">', f'id="blog-grid">\n{marker}\n{new_card}')
    
    with open(blog_file, "w") as f: f.write(updated)

def generate_post():
    topics = {"تنشيف": "أسرار التنشيف السريع", "تضخيم": "تضخيم العضلات في المنزل"}
    cat = random.choice(list(topics.keys()))
    title = topics[cat]
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال رياضي عن {title}"}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(100, 999)}.html"
        img = get_gym_image(cat)
        
        # إنشاء صفحة المقال
        with open(slug, "w") as f:
            f.write(f'<html><body style="direction:rtl; text-align:right; font-family:sans-serif; padding:50px;"><h1>{title}</h1><img src="{img}" style="width:100%">{body}</body></html>')
        
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        trigger_vercel_deploy()
        print(f"✅ تم بنجاح: {slug}")
    except Exception as e: print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    generate_post()
