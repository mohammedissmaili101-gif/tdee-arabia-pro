import os
import random
import datetime
import re
import requests
from groq import Groq

# 1. الإعدادات الأساسية
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia.vercel.app"
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

paragraph_styles = [
    "bg-blue-50 border-blue-200 text-blue-900",
    "bg-slate-50 border-slate-200 text-slate-900",
    "bg-indigo-50 border-indigo-200 text-indigo-900",
    "bg-emerald-50 border-emerald-200 text-emerald-900"
]

def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK)
            print("🚀 Vercel Deploy Triggered!")
        except Exception as e:
            print(f"⚠️ Vercel Error: {e}")

def get_gym_image():
    random_id = random.randint(1, 3000)
    return f"https://loremflickr.com/1200/800/gym,fitness,workout/all?lock={random_id}"

# 2. وظيفة الأرشفة التلقائية (Sitemap)
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
            new_entry = f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>\n"
            updated = content.replace("</urlset>", new_entry + "</urlset>")
            with open(sitemap_file, "w", encoding="utf-8") as f: f.write(updated)
    print(f"✅ Sitemap Updated: {url}")

def format_content(text):
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-3xl font-black text-blue-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-blue-100 py-4 rounded-l-2xl shadow-sm">{title}</h2>'
        elif p.startswith('* '):
            item = p.replace('* ', '')
            formatted_html += f'<div class="flex items-center gap-3 mb-4 p-4 bg-white rounded-xl border-r-4 border-blue-400 shadow-sm"><span class="text-2xl">⚡</span><p class="font-bold text-slate-700">{item}</p></div>'
        else:
            style = random.choice(paragraph_styles)
            formatted_html += f'<div class="p-8 rounded-[2rem] border-2 {style} shadow-sm leading-[2.3rem] text-xl mb-6">{p}</div>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    marker = ''
    
    new_card = f"""
    <div class="blog-card bg-white rounded-[2.5rem] shadow-xl overflow-hidden hover:scale-105 transition-all duration-500 border border-slate-100 group" data-category="{category}">
        <div class="relative overflow-hidden h-64">
            <img src="{image_url}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt="{title}">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-lg">{category}</div>
        </div>
        <div class="p-8 text-right">
            <span class="text-blue-500 font-bold text-sm">{today}</span>
            <h3 class="post-title text-2xl font-black mt-3 mb-6 text-slate-900 leading-tight h-20 overflow-hidden">{title}</h3>
            <a href="./{file_slug}" class="inline-block w-full text-center bg-slate-900 text-white font-bold py-4 rounded-2xl hover:bg-blue-600 transition-all shadow-lg">قراءة المقال ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo'}} .hidden{{display:none}}</style></head>
        <body class="bg-slate-50 text-right">
            <nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm p-6"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="font-bold text-slate-600">الرئيسية</a></div></nav>
            <main class="max-w-6xl mx-auto px-4 mt-10 text-center">
                <h2 class="text-5xl font-black text-slate-900 mb-10">المدونة الرياضية</h2>
                <div class="flex flex-wrap justify-center gap-4 mb-8">
                    <input type="text" id="searchInput" placeholder="ابحث عن مقال..." class="px-6 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 outline-none w-full max-w-md shadow-sm">
                </div>
                <div class="flex flex-wrap justify-center gap-3 mb-12">
                    <button onclick="filterBlog('all')" class="bg-slate-900 text-white px-6 py-2 rounded-full font-bold hover:bg-blue-600 transition-all">الكل</button>
                    <button onclick="filterBlog('تنشيف')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold border hover:border-blue-600 transition-all">تنشيف</button>
                    <button onclick="filterBlog('تضخيم')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold border hover:border-blue-600 transition-all">تضخيم</button>
                    <button onclick="filterBlog('مكملات')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold border hover:border-blue-600 transition-all">مكملات</button>
                </div>
                <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-32">
                    {marker}
                    {new_card}
                </div>
            </main>
            <script>
                function filterBlog(cat) {{
                    document.querySelectorAll('.blog-card').forEach(card => {{
                        if(cat === 'all' || card.getAttribute('data-category') === cat) card.classList.remove('hidden');
                        else card.classList.add('hidden');
                    }});
                }}
                document.getElementById('searchInput').addEventListener('input', (e) => {{
                    const term = e.target.value.toLowerCase();
                    document.querySelectorAll('.blog-card').forEach(card => {{
                        const title = card.querySelector('.post-title').innerText.toLowerCase();
                        card.classList.toggle('hidden', !title.includes(term));
                    }});
                }});
            </script>
        </body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated_content = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated_content)
        else:
            grid_start = '<div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-32">'
            updated_content = content.replace(grid_start, f"{grid_start}\n{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated_content)

def generate_post():
    categories = {"تنشيف": ["تنشيف الجسم", "حرق الدهون"], "تضخيم": ["تضخيم العضلات", "الضخامة العضلية"], "مكملات": ["واي بروتين", "كرياتين"]}
    cat_key = random.choice(list(categories.keys()))
    title = f"{random.choice(categories[cat_key])} لوزن {random.randint(60, 110)} كجم"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي بالعربية عن {title}. استعمل عناوين واضحة."}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = get_gym_image()
        
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo'}}</style></head>
        <body class="bg-slate-100"><nav class="bg-white/90 backdrop-blur-md sticky top-0 z-50 p-5 shadow-sm border-b"><div class="max-w-5xl mx-auto flex justify-between items-center"><a href="./blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a><span class="font-black text-2xl text-slate-900">TDEE ARABIA 🔥</span></div></nav>
        <main class="max-w-4xl mx-auto my-10 px-4">
            <div class="relative h-[400px] rounded-[3rem] overflow-hidden shadow-2xl mb-[-80px] z-10 border-8 border-white"><img src="{img}" class="w-full h-full object-cover"><div class="absolute inset-0 bg-black/40 flex items-center justify-center p-6"><h1 class="text-white text-4xl md:text-6xl font-black text-center">{title}</h1></div></div>
            <article class="bg-white pt-24 pb-16 px-8 rounded-[4rem] shadow-xl relative z-0 leading-loose">{body}</article>
        </main></body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat_key)
        update_sitemap(slug)  # 👈 هادي هي الأرشفة التلقائية
        trigger_vercel_deploy()
        print(f"✅ Post Generated and Indexed: {slug}")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
