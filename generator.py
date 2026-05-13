import os
import random
import datetime
import re
from groq import Groq

# الإعدادات الأساسية
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    footer = '</urlset>'
    url_entry = f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    
    if not os.path.exists(sitemap_file):
        content = header + f'  <url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>\n' + url_entry + footer
        with open(sitemap_file, "w", encoding="utf-8") as f: f.write(content)
    else:
        with open(sitemap_file, "r", encoding="utf-8") as f: content = f.read()
        if url not in content:
            # كنحيدو الـ footer القديم ونزيدو الرابط والـ footer من جديد
            content = content.replace(footer, "")
            updated = content + url_entry + footer
            with open(sitemap_file, "w", encoding="utf-8") as f: f.write(updated)

def format_content(text):
    # تنظيف وتنسيق النص
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-2xl font-black text-slate-800 mt-8 mb-4 border-r-4 border-blue-600 pr-3 text-right">{title}</h2>'
        else:
            formatted_html += f'<p class="text-lg text-slate-700 leading-relaxed mb-6 text-right">{p}</p>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    marker = 'HERE_IS_THE_LIST_MARKER'
    # استعملنا الرابط الكامل DOMAIN باش نحيدو الـ 404 نهائياً
    full_post_url = f"{DOMAIN}/{file_slug}"
    
    new_card = f'''
    <div class="blog-card bg-white rounded-3xl shadow-md hover:shadow-xl transition-all border border-slate-100 overflow-hidden" data-title="{title}">
        <img src="{image_url}" class="w-full h-52 object-cover">
        <div class="p-6 text-right">
            <span class="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-xs font-bold">{category}</span>
            <h3 class="text-xl font-bold mt-3 mb-4 text-slate-900">{title}</h3>
            <a href="{full_post_url}" class="inline-block w-full text-center bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-slate-900 transition-all">إقرأ المقال ←</a>
        </div>
    </div>'''
    
    if not os.path.exists(blog_file):
        initial_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}}</style></head><body class="bg-slate-50"><nav class="bg-white p-6 shadow-sm border-b sticky top-0 z-50"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><input type="text" id="searchInput" onkeyup="searchPosts()" placeholder="إبحث..." class="w-64 px-4 py-2 rounded-xl border outline-none text-right"></div></nav><main class="max-w-7xl mx-auto px-6 py-12"><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">{marker}{new_card}</div></main><script>function searchPosts() {{ let input = document.getElementById("searchInput").value.toLowerCase(); let cards = document.querySelectorAll(".blog-card"); cards.forEach(card => {{ let title = card.getAttribute("data-title").toLowerCase(); card.style.display = title.includes(input) ? "block" : "none"; }}); }}</script></body></html>'''
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    sport_keywords = ["gym", "fitness", "workout", "protein", "muscle"]
    topics = {"تنشيف": "أسرار التنشيف العضلي", "تضخيم": "دليل التضخيم الشامل", "تغذية": "أفضل وجبات قبل التمرين"}
    cat = random.choice(list(topics.keys()))
    title = topics[cat] + f" لعام {random.randint(2025, 2026)}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي مطول جدا بالعربية عن {title}. استعمل عناوين واضحة."}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = f"https://loremflickr.com/800/600/{random.choice(sport_keywords)}/all?lock={random.randint(1,1000)}"
        
        full_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}}</style></head><body class="bg-slate-50"><article class="max-w-4xl mx-auto py-16 px-6 bg-white min-h-screen shadow-lg rounded-3xl mt-10"><a href="./blog.html" class="text-blue-600 font-bold mb-8 inline-block hover:underline">← العودة للمدونة</a><img src="{img}" class="w-full h-96 object-cover rounded-2xl mb-8"><h1 class="text-4xl font-black mb-8 text-slate-900 border-b-4 border-blue-600 pb-4 text-right">{title}</h1><div class="content">{body}</div></article></body></html>'''
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        print(f"✅ تم بنجاح: {slug}")
    except Exception as e: print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    generate_post()
