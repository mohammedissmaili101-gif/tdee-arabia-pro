import os
import random
import datetime
import re
import requests
from groq import Groq

# الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def get_pexels_image(query):
    """جلب صورة احترافية من Pexels مرتبطة بالموضوع"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=15&orientation=landscape"
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("photos"):
            # اختيار صورة عشوائية من النتائج الأولى لضمان التنوع
            return random.choice(data["photos"])["src"]["large2x"]
    except Exception as e:
        print(f"Pexels Error: {e}")
    # صورة احتياطية في حالة فشل الـ API
    return "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg"

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
            updated = content.replace(footer, url_entry + footer)
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
            formatted_html += f'<h2 class="text-3xl font-black text-slate-800 mt-14 mb-8 border-r-[10px] border-blue-600 pr-5 bg-gradient-to-l from-blue-50 to-transparent py-4 rounded-l-3xl text-right leading-tight">{title}</h2>'
        elif p.startswith('* '):
            item = p.replace('* ', '')
            formatted_html += f'<li class="text-lg text-slate-700 mb-4 list-none flex items-center justify-end gap-3"><span class="font-medium">{item}</span><span class="w-2 h-2 bg-blue-500 rounded-full"></span></li>'
        else:
            formatted_html += f'<p class="text-xl text-slate-700 leading-loose mb-10 text-right font-light bg-white p-2">{p}</p>'
    return formatted_html

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    marker = 'HERE_IS_THE_LIST_MARKER'
    full_post_url = f"{DOMAIN}/{file_slug}"
    read_time = random.randint(5, 12)
    
    new_card = f'''
    <div class="blog-card group bg-white rounded-[3rem] shadow-sm hover:shadow-2xl transition-all duration-500 border border-slate-100 overflow-hidden" data-title="{title}">
        <div class="relative overflow-hidden">
            <img src="{image_url}" class="w-full h-80 object-cover group-hover:scale-105 transition-transform duration-700">
            <div class="absolute top-6 right-6 bg-blue-600 text-white px-5 py-2 rounded-2xl text-xs font-black tracking-widest uppercase">{category}</div>
        </div>
        <div class="p-10 text-right">
            <div class="flex justify-end gap-4 text-slate-400 text-xs mb-4 font-bold">
                <span>• {read_time} MIN READ</span>
                <span>MAGAZINE EDITION</span>
            </div>
            <h3 class="text-2xl font-black mb-6 text-slate-900 leading-snug group-hover:text-blue-600 transition-colors">{title}</h3>
            <a href="{full_post_url}" class="inline-flex items-center gap-2 text-blue-600 font-black text-sm uppercase tracking-wider group-hover:gap-4 transition-all underline underline-offset-8">إقرأ المقال الكامل ←</a>
        </div>
    </div>'''
    
    if os.path.exists(blog_file):
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    # نظام توليد مواضيع لا نهائي
    themes = {
        "كمال أجسام": ["تضخيم عضلة الصدر", "تنشيف البطن", "تقوية الظهر", "تمارين الكتاف", "بناء الأرجل"],
        "تغذية": ["بروتين طبيعي", "وجبات الكيتو", "الصيام المتقطع", "كربوهيدرات معقدة", "مكملات الكرياتين"],
        "أسلوب حياة": ["تحسين النوم للرياضيين", "تجنب الإصابات", "التحفيز الذهني", "تمارين التمدد", "HIIT للقلب"]
    }
    
    modifiers = ["دليل شامل للمبتدئين", "أسرار المحترفين", "أخطاء شائعة تجنبها", "أفضل الطرق العلمية لـ", "كيفية تطوير"]
    
    cat = random.choice(list(themes.keys()))
    base_topic = random.choice(themes[cat])
    modifier = random.choice(modifiers)
    title = f"{modifier} {base_topic}"
    
    # تحديد الكلمة البحثية للصور بناءً على الموضوع
    search_query = base_topic.replace(" ", "+") + "+fitness"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال مجلة رياضية احترافي جدا وبأسلوب بشري مشوق عن {title}. المقال يجب أن يحتوي على: مقدمة قوية، عناوين فرعية بين **، قائمة نصائح عملية، وخاتمة ملهمة. استخدم لغة عربية سليمة ومحفزة."}],
            model="llama-3.3-70b-versatile"
        )
        
        body = format_content(response.choices[0].message.content)
        img = get_pexels_image(search_query)
        slug = f"article-{random.randint(100000, 999999)}.html"
        
        full_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}}</style></head><body class="bg-slate-50"><article class="max-w-5xl mx-auto py-20 px-8 bg-white min-h-screen shadow-2xl rounded-[4rem] my-12 border border-slate-100"><div class="mb-12 text-center"><span class="text-blue-600 font-black tracking-widest uppercase text-sm">{cat}</span><h1 class="text-5xl md:text-7xl font-black mt-6 mb-10 text-slate-900 leading-tight text-right">{title}</h1><div class="w-32 h-2 bg-blue-600 mr-0 ml-auto rounded-full"></div></div><img src="{img}" class="w-full h-[600px] object-cover rounded-[4rem] mb-16 shadow-2xl"><div class="content max-w-3xl mx-auto text-right">{body}</div><div class="mt-20 p-16 bg-slate-900 rounded-[4rem] text-center text-white"><h4 class="text-3xl font-black mb-6 italic">TDEE ARABIA 🔥</h4><a href="{DOMAIN}/blog.html" class="inline-block bg-blue-600 px-12 py-5 rounded-3xl font-black hover:bg-blue-700 transition-all text-xl">العودة للمجلة</a></div></article></body></html>'''
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        print(f"🚀 Published via Pexels: {slug}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
