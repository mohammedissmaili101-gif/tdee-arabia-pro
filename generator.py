import os
import random
import datetime
import re
from groq import Groq

# 1. الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def format_content(text):
    # تنظيف وتنسيق النص القادم من AI
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-3xl font-black text-slate-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-slate-100 py-4 rounded-l-2xl text-right">{title}</h2>'
        else:
            formatted_html += f'<div class="p-6 rounded-2xl bg-slate-50 border border-slate-100 shadow-sm leading-relaxed text-xl mb-6 text-right text-slate-700">{p}</div>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    marker = 'HERE_IS_THE_LIST_MARKER'
    
    # الكارت مع رابط مباشر وصحيح
    new_card = f"""
    <div class="blog-card bg-white rounded-[2.5rem] shadow-sm hover:shadow-xl transition-all border border-slate-100 overflow-hidden" data-title="{title}">
        <img src="{image_url}" class="w-full h-64 object-cover">
        <div class="p-8 text-right">
            <span class="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-xs font-bold">{category}</span>
            <h3 class="text-xl font-black mt-4 mb-6 text-slate-900">{title}</h3>
            <a href="./{file_slug}" class="block w-full text-center bg-slate-900 text-white font-bold py-4 rounded-2xl hover:bg-blue-600 transition-all">إقرأ المقال ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>مدونة TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50">
            <nav class="bg-white p-6 shadow-sm sticky top-0 z-50 border-b">
                <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1>
                    <input type="text" id="searchInput" onkeyup="searchPosts()" placeholder="إبحث عن مقال..." class="w-full md:w-96 px-5 py-3 rounded-2xl border border-slate-200 outline-none text-right focus:ring-2 focus:ring-blue-500">
                </div>
            </nav>
            <main class="max-w-7xl mx-auto px-6 py-12">
                <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {marker}
                    {new_card}
                </div>
            </main>
            <script>
                function searchPosts() {{
                    let input = document.getElementById('searchInput').value.toLowerCase();
                    let cards = document.querySelectorAll('.blog-card');
                    cards.forEach(card => {{
                        let title = card.getAttribute('data-title').toLowerCase();
                        card.style.display = title.includes(input) ? "block" : "none";
                    }});
                }}
            </script>
        </body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    img_keywords = ["gym", "fitness", "workout", "bodybuilding", "protein"]
    topics = {"تنشيف": "أسرار التنشيف العضلي", "تضخيم": "دليل التضخيم الشامل", "تغذية": "أفضل وجبات قبل التمرين"}
    cat = random.choice(list(topics.keys()))
    title = topics[cat] + f" {random.randint(2025, 2026)}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي مطول جدا بالعربية عن {title}"}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = f"https://loremflickr.com/800/600/{random.choice(img_keywords)}?lock={random.randint(1,999)}"
        
        # تصميم صفحة المقال (التعديل المهم هنا لعدم ظهور 404)
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50">
            <article class="max-w-4xl mx-auto py-16 px-6 bg-white shadow-sm min-h-screen">
                <a href="./blog.html" class="text-blue-600 font-bold mb-8 inline-block hover:underline">← العودة للمدونة</a>
                <img src="{img}" class="w-full h-96 object-cover rounded-3xl shadow-lg mb-12">
                <h1 class="text-4xl md:text-5xl font-black mb-10 text-slate-900 leading-tight">{title}</h1>
                <div class="prose prose-xl max-w-none">
                    {body}
                </div>
            </article>
        </body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        print(f"✅ تم إنشاء المقال بنجاح: {slug}")
        
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
