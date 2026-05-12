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

# تنسيقات الفقرات
paragraph_styles = [
    "bg-blue-50 border-blue-200 text-blue-900",
    "bg-slate-50 border-slate-200 text-slate-900",
    "bg-indigo-50 border-indigo-200 text-indigo-900",
    "bg-emerald-50 border-emerald-200 text-emerald-900"
]

# FIX 3: loremflickr غير موثوق - استبدلناه بـ picsum مع seed ثابت لكل category
def get_gym_image(category):
    seeds = {
        "تنشيف":        [10, 20, 30, 40, 50],
        "تضخيم":        [60, 70, 80, 90, 100],
        "مكملات":       [110, 120, 130, 140, 150],
        "تغذية":        [160, 170, 180, 190, 200],
        "تمارين منزلية": [210, 220, 230, 240, 250],
    }
    seed = random.choice(seeds.get(category, [300, 310, 320]))
    return f"https://picsum.photos/seed/{seed}/1200/800"


def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK)
            print("🚀 Vercel Deploy Triggered!")
        except Exception as e:
            print(f"⚠️ Vercel Error: {e}")


def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(sitemap_file):
        content = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>'
            f'<url><loc>{DOMAIN}/blog.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>'
            f'<url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>'
            '</urlset>'
        )
        with open(sitemap_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(sitemap_file, "r", encoding="utf-8") as f:
            content = f.read()
        if url not in content:
            updated = content.replace(
                "</urlset>",
                f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>\n</urlset>"
            )
            with open(sitemap_file, "w", encoding="utf-8") as f:
                f.write(updated)


# FIX 2: كنا نمسحو الأرقام الإنجليزية - صلحنا regex باش يحتفظ بـ \d
def format_content(text):
    # نحتفظ بالعربية + spaces + أرقام + علامات الترقيم الأساسية
    text = re.sub(r'[^\u0600-\u06FF\s\d.,:\-!?()*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += (
                f'<h2 class="text-3xl font-black text-blue-800 mt-12 mb-6 '
                f'border-r-8 border-blue-600 pr-4 bg-blue-100 py-4 rounded-l-2xl text-right">'
                f'{title}</h2>'
            )
        elif p.startswith('* '):
            item = p.replace('* ', '', 1)
            formatted_html += (
                f'<div class="flex items-center gap-3 mb-4 p-4 bg-white rounded-xl '
                f'border-r-4 border-blue-400 text-right shadow-sm">'
                f'<span class="text-2xl">⚡</span>'
                f'<p class="font-bold text-slate-700">{item}</p></div>'
            )
        else:
            style = random.choice(paragraph_styles)
            formatted_html += (
                f'<div class="p-8 rounded-[2rem] border-2 {style} shadow-sm '
                f'leading-[2.3rem] text-xl mb-6 text-right font-medium">{p}</div>'
            )
    return formatted_html


def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")

    # FIX 1: marker فريد وواضح - مش string فارغ
    marker = '<!-- NEW_POSTS_HERE -->'

    new_card = f"""
    <div class="blog-card bg-white rounded-[2.5rem] shadow-xl overflow-hidden hover:scale-105 transition-all duration-500 border border-slate-100 group" data-category="{category}">
        <div class="relative h-64">
            <img src="{image_url}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt="{title}">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-lg">{category}</div>
        </div>
        <div class="p-8 text-right">
            <span class="text-blue-500 font-bold text-sm">{today}</span>
            <h3 class="post-title text-2xl font-black mt-3 mb-6 text-slate-900 leading-tight h-24 overflow-hidden">{title}</h3>
            <a href="./{file_slug}" class="inline-block w-full text-center bg-slate-900 text-white font-bold py-4 rounded-2xl hover:bg-blue-600 transition-all shadow-lg">قراءة المقال ←</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        # FIX 4: نضمن أن marker موجود داخل blog.html الجديد
        initial_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>المدونة | TDEE Arabia</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
  <style>body{{font-family:'Cairo'}}</style>
</head>
<body class="bg-slate-50">
  <nav class="bg-white p-6 shadow-sm sticky top-0 z-50 text-right">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1>
      <a href="/" class="font-bold text-slate-600">الرئيسية</a>
    </div>
  </nav>
  <main class="max-w-6xl mx-auto px-4 mt-10">
    <div class="text-center mb-12">
      <h2 class="text-5xl font-black text-slate-900 mb-8 italic">المدونة الرياضية الشاملة</h2>
      <div class="flex justify-center">
        <input type="text" id="searchInput" placeholder="ابحث عن موضوع..."
          class="px-6 py-4 rounded-2xl border-2 border-slate-200 focus:border-blue-500 outline-none w-full max-w-md shadow-lg text-right">
      </div>
      <div class="flex flex-wrap justify-center gap-3 mt-6">
        <button onclick="filterBlog('all')" class="bg-slate-900 text-white px-8 py-2 rounded-full font-bold shadow-md">الكل</button>
        <button onclick="filterBlog('تنشيف')" class="bg-white border px-8 py-2 rounded-full font-bold hover:bg-blue-600 hover:text-white transition-all">تنشيف</button>
        <button onclick="filterBlog('تضخيم')" class="bg-white border px-8 py-2 rounded-full font-bold hover:bg-blue-600 hover:text-white transition-all">تضخيم</button>
        <button onclick="filterBlog('تغذية')" class="bg-white border px-8 py-2 rounded-full font-bold hover:bg-blue-600 hover:text-white transition-all">تغذية</button>
        <button onclick="filterBlog('مكملات')" class="bg-white border px-8 py-2 rounded-full font-bold hover:bg-blue-600 hover:text-white transition-all">مكملات</button>
        <button onclick="filterBlog('تمارين منزلية')" class="bg-white border px-8 py-2 rounded-full font-bold hover:bg-blue-600 hover:text-white transition-all">تمارين منزلية</button>
      </div>
    </div>
    <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-32">
      {marker}
      {new_card}
    </div>
  </main>
  <script>
    function filterBlog(cat) {{
      document.querySelectorAll('.blog-card').forEach(c => {{
        c.style.display = (cat === 'all' || c.dataset.category === cat) ? 'block' : 'none';
      }});
    }}
    document.getElementById('searchInput').addEventListener('input', (e) => {{
      const t = e.target.value.toLowerCase();
      document.querySelectorAll('.blog-card').forEach(c => {{
        const title = c.querySelector('.post-title').innerText.toLowerCase();
        c.style.display = title.includes(t) ? 'block' : 'none';
      }});
    }});
  </script>
</body>
</html>"""
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f:
            content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(updated)
        else:
            # fallback: إذا marker مش موجود في ملف قديم - نضيفه قبل </div> الأخير
            updated = content.replace(
                '</div>\n  </main>',
                f'{marker}\n{new_card}\n</div>\n  </main>'
            )
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(updated)


def generate_post():
    topics = {
        "تنشيف":          ["حرق دهون الكرش", "رجيم التنشيف القاسي", "تمارين الكارديو للتنشيف"],
        "تضخيم":          ["تضخيم عضلات الصدر", "أقوى برنامج ضخامة عضلية", "كيف تزيد وزنك عضل"],
        "تغذية":          ["وجبات قبل التمرين", "أفضل مصادر البروتين الطبيعية", "نظام غذائي صحي"],
        "مكملات":         ["مراجعة واي بروتين", "فوائد الكرياتين للرياضيين", "أفضل مكملات الطاقة"],
        "تمارين منزلية": ["تمارين منزلية بدون أثقال", "شد الجسم في المنزل", "تمارين البطن للمبتدئين"],
    }
    cat_key = random.choice(list(topics.keys()))
    topic_title = random.choice(topics[cat_key])
    title = f"{topic_title} - دليل 2026"

    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"اكتب مقال SEO رياضي احترافي بالعربية عن {title}. استعمل عناوين واضحة ونقاط."
            }],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = get_gym_image(cat_key)

        full_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
  <style>body{{font-family:'Cairo'}}</style>
</head>
<body class="bg-slate-100">
  <nav class="bg-white p-5 shadow-sm border-b sticky top-0 z-50 text-right">
    <div class="max-w-5xl mx-auto flex justify-between items-center">
      <a href="./blog.html" class="text-blue-600 font-bold">← المدونة</a>
      <span class="font-black text-2xl text-slate-900">TDEE ARABIA 🔥</span>
    </div>
  </nav>
  <main class="max-w-4xl mx-auto my-10 px-4 text-right">
    <div class="relative h-[450px] rounded-[3rem] overflow-hidden shadow-2xl mb-[-80px] z-10 border-8 border-white">
      <img src="{img}" class="w-full h-full object-cover">
      <div class="absolute inset-0 bg-black/40 flex items-end p-12">
        <h1 class="text-white text-5xl font-black leading-tight">{title}</h1>
      </div>
    </div>
    <article class="bg-white pt-32 pb-16 px-10 rounded-[4rem] shadow-xl relative z-0">
      {body}
    </article>
  </main>
</body>
</html>"""

        with open(slug, "w", encoding="utf-8") as f:
            f.write(full_html)
        update_blog_list(slug, title, img, cat_key)
        update_sitemap(slug)
        trigger_vercel_deploy()
        print(f"✅ تم إنشاء المقال: {slug}")
    except Exception as e:
        print(f"❌ خطأ: {e}")


if __name__ == "__main__":
    generate_post()
