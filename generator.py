import os
import random
import datetime
import re
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOMAIN = "https://tdee-arabia.vercel.app"

# صور متنوعة واحترافية مع روابط احتياطية مدمجة في HTML
gym_images = [
    "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "https://images.pexels.com/photos/949126/pexels-photo-949126.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "https://images.pexels.com/photos/2261477/pexels-photo-2261477.jpeg?auto=compress&cs=tinysrgb&w=1200"
]

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

def format_content(text):
    # تحويل العناوين ** لجعلها ضخمة وملونة
    text = re.sub(r'\*\*(.*?)\*\*', r'<h2 class="text-3xl font-black text-blue-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-blue-50 py-3 rounded-l-xl">\1</h2>', text)
    text = text.replace('\n', '<br>')
    return text

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    new_card = f"""
    <div class="blog-card bg-white rounded-[2.5rem] shadow-xl overflow-hidden hover:scale-105 transition-all duration-500 border border-slate-100 group" data-category="{category}">
        <div class="relative overflow-hidden h-64">
            <img src="{image_url}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" onerror="this.src='https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=800'">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-lg">{category}</div>
        </div>
        <div class="p-8 text-right">
            <span class="text-blue-500 font-bold text-sm">{today}</span>
            <h3 class="post-title text-2xl font-black mt-3 mb-6 text-slate-900 leading-tight h-20 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="inline-block w-full text-center bg-slate-900 text-white font-bold py-4 rounded-2xl hover:bg-blue-600 transition-all shadow-lg">قراءة المقال ←</a>
        </div>
    </div>
    """
    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>.hidden {{ display: none; }} body{{font-family:'Cairo'}}</style></head>
        <body class="bg-slate-50 text-right"><nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm p-6"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="font-bold text-slate-600">الرئيسية</a></div></nav>
        <main class="max-w-6xl mx-auto px-4 mt-16"><div class="text-center mb-16"><h2 class="text-6xl font-black mb-8 text-slate-900 underline decoration-blue-600 decoration-8 underline-offset-8">المدونة الرياضية</h2>
        <div class="max-w-2xl mx-auto mb-10"><input type="text" id="searchInput" placeholder="ابحث عن موضوعك الرياضي..." class="w-full p-6 rounded-3xl border-none shadow-2xl focus:ring-4 focus:ring-blue-500 outline-none text-xl transition-all"></div>
        <div class="flex flex-wrap justify-center gap-4"><button onclick="filterPosts('الكل')" class="bg-blue-600 text-white px-8 py-3 rounded-full font-black shadow-lg">الكل</button><button onclick="filterPosts('تنشيف')" class="bg-white text-slate-600 px-8 py-3 rounded-full font-black shadow-md hover:bg-blue-600 hover:text-white transition-all">تنشيف</button><button onclick="filterPosts('تضخيم')" class="bg-white text-slate-600 px-8 py-3 rounded-full font-black shadow-md hover:bg-blue-600 hover:text-white transition-all">تضخيم</button><button onclick="filterPosts('مكملات')" class="bg-white text-slate-600 px-8 py-3 rounded-full font-black shadow-md hover:bg-blue-600 hover:text-white transition-all">مكملات</button></div></div>
        <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 pb-32">{new_card}</div></main>
        <script>document.getElementById('searchInput').addEventListener('keyup', e=>{{let t=e.target.value.toLowerCase();document.querySelectorAll('.blog-card').forEach(c=>{{c.classList.toggle('hidden', !c.querySelector('.post-title').innerText.toLowerCase().includes(t))}})}});
        function filterPosts(cat){{document.querySelectorAll('.blog-card').forEach(c=>{{c.classList.toggle('hidden', cat!=='الكل' && c.getAttribute('data-category')!==cat)}})}}</script></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        marker = ''
        if marker in content:
            new_content = content.replace(marker, new_card, 1)
            with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    cats = {"تنشيف": ["حرق الدهون", "تنشيف الكرش"], "تضخيم": ["بناء العضلات", "تضخيم طبيعي"], "مكملات": ["بروتين", "كرياتين"]}
    category = random.choice(list(cats.keys()))
    title = f"{random.choice(cats[category])} لوزن {random.randint(60, 110)} كجم"
    image = random.choice(gym_images)
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": f"اكتب مقال SEO فخم جداً ومفصل بالعربية عن {title}. استخدم فقرات مشوقة وعناوين فرعية."}], model="llama-3.3-70b-versatile")
        body = format_content(res.choices[0].message.content)
        file_slug = f"post-{random.randint(10000, 99999)}.html"
        article_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo'}}</style></head>
        <body class="bg-slate-100"><nav class="bg-white/90 backdrop-blur-md sticky top-0 z-50 p-5 shadow-sm border-b"><div class="max-w-5xl mx-auto flex justify-between items-center"><a href="/blog.html" class="text-blue-600 font-bold">← المدونة</a><span class="font-black text-2xl">TDEE <span class="text-blue-600">ARABIA</span> 🔥</span></div></nav>
        <main class="max-w-4xl mx-auto my-10 px-4"><div class="relative h-[450px] rounded-[3rem] overflow-hidden shadow-2xl mb-[-80px] z-10 border-8 border-white"><img src="{image}" class="w-full h-full object-cover" onerror="this.src='https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=1200'"><div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div><div class="absolute bottom-12 right-12 text-white"><span class="bg-blue-600 px-4 py-1 rounded-full text-sm font-bold mb-4 inline-block">{category}</span><h1 class="text-4xl md:text-6xl font-black leading-tight">{title}</h1></div></div>
        <article class="bg-white pt-28 pb-16 px-8 md:px-20 rounded-[4rem] shadow-xl relative z-0"><div class="text-xl leading-[2.2rem] text-slate-700 space-y-8">{body}</div></article></main></body></html>"""
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        update_blog_list(file_slug, title, image, category)
        update_sitemap(file_slug)
        print(f"✅ تم بنجاح: {title}")
    except Exception as e: print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    generate()
