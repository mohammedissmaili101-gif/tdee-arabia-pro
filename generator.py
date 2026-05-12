import os
import random
import datetime
import re
from groq import Groq

# 1. الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    marker = 'HERE_IS_THE_LIST_MARKER'
    
    # تصميم الكارت (Card) بشكل احترافي
    new_card = f"""
    <div class="blog-card bg-white rounded-3xl shadow-sm hover:shadow-2xl transition-all duration-300 overflow-hidden border border-slate-100 group" data-title="{title}">
        <div class="relative overflow-hidden">
            <img src="{image_url}" class="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-500">
            <span class="absolute top-4 right-4 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-bold">{category}</span>
        </div>
        <div class="p-8 text-right">
            <span class="text-slate-400 text-sm">{today}</span>
            <h3 class="text-xl font-black mt-2 mb-6 text-slate-900 h-14 overflow-hidden">{title}</h3>
            <a href="./{file_slug}" class="block w-full text-center bg-slate-900 text-white font-bold py-4 rounded-xl hover:bg-blue-600 transition-colors">إقرأ التفاصيل ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>مدونة TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}} .blog-card{{display:block;}}</style></head>
        <body class="bg-slate-50">
            <nav class="bg-white p-6 shadow-sm sticky top-0 z-50 border-b">
                <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1>
                    <div class="relative w-full md:w-96">
                        <input type="text" id="searchInput" onkeyup="searchPosts()" placeholder="إبحث عن مقال..." class="w-full px-5 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none text-right">
                    </div>
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
                    let cards = document.getElementsByClassName('blog-card');
                    for (let card of cards) {{
                        let title = card.getAttribute('data-title').toLowerCase();
                        card.style.display = title.includes(input) ? "block" : "none";
                    }}
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
    # كلمات دلالية للصور (احترافية)
    img_keywords = ["bodybuilding", "fitness-model", "gym-workout", "healthy-food", "crossfit"]
    topics = {"تنشيف": "أسرار حرق الدهون", "تضخيم": "أقوى نظام تضخيم", "تغذية": "وجبات البروتين"}
    cat = random.choice(list(topics.keys()))
    title = topics[cat] + f" {random.randint(2025, 2026)}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي مطول بالعربية عن {title}"}],
            model="llama-3.3-70b-versatile"
        )
        # تنسيق المحتوى (نفس الدالة السابقة)
        body = response.choices[0].message.content # غتحتاج دالة format_content اللي عندك
        
        slug = f"post-{random.randint(10000, 99999)}.html"
        # رابط صور احترافي
        img = f"https://loremflickr.com/800/600/{random.choice(img_keywords)}?lock={random.randint(1,1000)}"
        
        # إنشاء صفحة المقال بتصميم متناسق
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-white">
            <article class="max-w-4xl mx-auto py-16 px-6">
                <a href="./blog.html" class="text-blue-600 font-bold mb-8 inline-block">← العودة للمدونة</a>
                <img src="{img}" class="w-full h-[450px] object-cover rounded-[2rem] shadow-xl mb-12">
                <h1 class="text-4xl md:text-6xl font-black mb-10 text-slate-900 leading-tight">{title}</h1>
                <div class="prose prose-xl max-w-none text-slate-700 leading-relaxed text-right">
                    {body} 
                </div>
            </article>
        </body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        print(f"✅ تم بنجاح: {slug}")
        
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
