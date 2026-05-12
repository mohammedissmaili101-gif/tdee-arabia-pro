import os
import random
import datetime
import re
import requests
from groq import Groq

# 1. الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app"
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

# 2. ثوابت التنسيق
paragraph_styles = [
    "bg-white border-r-4 border-blue-500 text-slate-800",
    "bg-blue-50 border-r-4 border-indigo-400 text-indigo-900",
    "bg-slate-50 border-r-4 border-slate-400 text-slate-900",
    "bg-emerald-50 border-r-4 border-emerald-400 text-emerald-900"
]

# الماركر الصحيح (تعليق HTML مخفي)
MARKER = "<!-- BLOG_POSTS_MARKER -->"

# 3. دوال المساعدة
def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK, timeout=10)
            print("🚀 تم إرسال إشارة النشر إلى Vercel")
        except Exception as e:
            print(f"⚠️ فشل تنشيط Vercel: {e}")

def update_sitemap(file_slug):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(sitemap_file):
        content = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod></url></urlset>'
        with open(sitemap_file, "w", encoding="utf-8") as f:
            f.write(content)
    
    with open(sitemap_file, "r", encoding="utf-8") as f:
        content = f.read()
    if url not in content:
        updated = content.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>\n</urlset>")
        with open(sitemap_file, "w", encoding="utf-8") as f:
            f.write(updated)

def format_content(text):
    # تنظيف النص من الرموز غير العربية
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-3xl font-black text-slate-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-slate-100 py-4 rounded-l-2xl shadow-sm text-right">{title}</h2>'
        else:
            style = random.choice(paragraph_styles)
            formatted_html += f'<div class="p-8 rounded-[2.5rem] border {style} shadow-sm leading-[2.6rem] text-xl mb-8 font-medium text-right">{p}</div>'
    return formatted_html

def ensure_blog_exists():
    """تضمن وجود ملف blog.html بالماركر الصحيح، حتى لو كان الملف موجوداً وتالفاً"""
    blog_file = "blog.html"
    if not os.path.exists(blog_file):
        # إنشاء ملف جديد من الصفر
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>TDEE Arabia Blog</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
<body class="bg-slate-50">
    <nav class="bg-white p-6 shadow-sm border-b"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</h1></div></nav>
    <main class="max-w-7xl mx-auto px-6 py-16 text-right">
        <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
            {MARKER}
        </div>
    </main>
</body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(initial_html)
        print("📄 تم إنشاء blog.html جديد")
        return

    # الملف موجود → تأكد من وجود الماركر الصحيح
    with open(blog_file, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        # الماركر موجود، لا حاجة لتعديل
        print("✓ blog.html سليم والماركر موجود")
        return

    # الماركر مفقود أو تالف → نصلح الملف مع الاحتفاظ بالبطاقات القديمة إن وجدت
    print("⚠️ الماركر غير موجود في blog.html، جاري إصلاحه...")
    old_cards = ""
    # استخراج كل العناصر التي تشبه بطاقة المقال (حتى لو كانت بدون الماركر)
    card_pattern = r'(<div class="blog-card.*?</div>\s*</div>)'
    cards = re.findall(card_pattern, content, re.DOTALL)
    if cards:
        old_cards = "\n".join(cards) + "\n"
        print(f"  ↳ تم استرداد {len(cards)} بطاقة قديمة")

    # بناء ملف جديد بالماركر والبطاقات القديمة
    new_content = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>TDEE Arabia Blog</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
<body class="bg-slate-50">
    <nav class="bg-white p-6 shadow-sm border-b"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</h1></div></nav>
    <main class="max-w-7xl mx-auto px-6 py-16 text-right">
        <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
            {old_cards}
            {MARKER}
        </div>
    </main>
</body></html>"""
    with open(blog_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ تم إصلاح blog.html ووضع الماركر الصحيح")

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    new_card = f"""
    <div class="blog-card bg-white rounded-[3rem] shadow-xl overflow-hidden mb-10 border border-slate-100">
        <img src="{image_url}" class="w-full h-72 object-cover">
        <div class="p-10 text-right">
            <span class="text-blue-500 font-bold">{today}</span>
            <h3 class="post-title text-2xl font-black mt-4 mb-8 text-slate-900">{title}</h3>
            <a href="./{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-black py-5 rounded-2xl hover:bg-slate-900 transition-all shadow-lg">إقرأ التفاصيل ←</a>
        </div>
    </div>"""

    ensure_blog_exists()  # يضمن وجود الماركر
    
    with open(blog_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # إضافة البطاقة الجديدة قبل الماركر مباشرة
    if MARKER in content:
        updated = content.replace(MARKER, f"{new_card}\n{MARKER}")
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"➕ أُضيف المقال: {title}")
    else:
        # حماية: في حالة اختفاء الماركر رغم ensure_blog_exists
        print("❌ خطأ: الماركر لا يزال مفقوداً رغم المحاولة!")
        # نضيف الماركر مع البطاقة في نهاية الـ grid
        updated = content.replace('id="blog-grid">', f'id="blog-grid">\n{new_card}\n{MARKER}')
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(updated)

def generate_post():
    print("🔄 بدء إنشاء مقال جديد...")
    ensure_blog_exists()  # الخطوة الأولى
    
    topics = {"تنشيف": "أسرار حرق الدهون", "تضخيم": "أقوى نظام تضخيم", "تغذية": "وجبات اقتصادية"}
    cat = random.choice(list(topics.keys()))
    title = f"{topics[cat]} 2026"
    
    try:
        print("📡 الاتصال بـ Groq API...")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي مطول بالعربية عن {title}"}],
            model="llama-3.3-70b-versatile"
        )
        body = format_content(response.choices[0].message.content)
        slug = f"post-{random.randint(10000, 99999)}.html"
        img = f"https://loremflickr.com/1200/800/gym/all?lock={random.randint(1,999)}"
        
        full_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo', sans-serif;}}</style></head>
        <body class="bg-slate-50 text-right">
            <main class="max-w-4xl mx-auto py-20 px-6">
                <a href="./blog.html" class="text-blue-600 font-bold mb-10 inline-block">← العودة للمدونة</a>
                <img src="{img}" class="w-full rounded-[3rem] shadow-2xl mb-12">
                <h1 class="text-5xl font-black mb-10 text-slate-900">{title}</h1>
                <article>{body}</article>
            </main>
        </body></html>"""
        
        with open(slug, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        trigger_vercel_deploy()
        print(f"✅ تم بنجاح: {slug}")
        
    except Exception as e:
        print(f"❌ فشل إنشاء المقال: {e}")
        # لا نعيد رفع الخطأ لأن المدونة موجودة على الأقل

if __name__ == "__main__":
    generate_post()
