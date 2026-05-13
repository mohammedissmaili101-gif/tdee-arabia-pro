import os
import random
import datetime
import re
from groq import Groq

# الإعدادات
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
            updated = content.replace(footer, url_entry + footer)
            with open(sitemap_file, "w", encoding="utf-8") as f: f.write(updated)

def format_content(text):
    # تنسيق "مجلة" بفقرات مريحة وعناوين بارزة
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
    
    if not os.path.exists(blog_file):
        initial_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}} .blog-card{{transition: transform 0.3s ease;}} .blog-card:hover{{transform: translateY(-8px);}}</style></head><body class="bg-slate-50"><nav class="bg-white/80 backdrop-blur-md p-8 shadow-sm border-b sticky top-0 z-50"><div class="max-w-7xl mx-auto flex justify-between items-center"><h1 class="text-3xl font-black tracking-tighter text-slate-900">TDEE <span class="text-blue-600 italic">ARABIA</span></h1><input type="text" id="searchInput" onkeyup="searchPosts()" placeholder="إبحث في المجلة..." class="w-72 px-6 py-4 rounded-[2rem] border-2 border-slate-100 outline-none focus:border-blue-600 transition-all text-right shadow-inner"></div></nav><main class="max-w-7xl mx-auto px-8 py-20"><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 text-right">{marker}{new_card}</div></main><script>function searchPosts() {{ let input = document.getElementById("searchInput").value.toLowerCase(); let cards = document.querySelectorAll(".blog-card"); cards.forEach(card => {{ let title = card.getAttribute("data-title").toLowerCase(); card.style.display = title.includes(input) ? "block" : "none"; }}); }}</script></body></html>'''
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    categories_keys = ["تغذية", "تدريب", "عقلية"]
    cat = random.choice(categories_keys)
    
    try:
        # تعديل البرومبت لضمان جلب كلمات دلالية بصرية وحقيقية متعلقة بالجيم فقط
        prompt = (f"أنت خبير في كمال الأجسام واللياقة البدنية. اكتب مقالاً كاملاً ومفصلاً في قسم '{cat}'. "
                  f"اجعل العنوان في أول سطر. ثم ابدأ المقال مباشرة. "
                  f"المقال يجب أن يكون بأسلوب بشري مشوق، يحتوي على مقدمة، عناوين فرعية بـ **، قائمة نصائح بـ * ، وخاتمة. "
                  f"في السطر الأخير تماماً، اكتب 3 كلمات إنجليزية فقط تصف 'صورة فوتوغرافية احترافية' داخل صالة الجيم أو لمعدات رياضية أو لاعب عضلات "
                  f"تناسب المقال (تجنب الكلمات المعنوية، نريد أشياء ملموسة تُصوّر).")

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        
        full_text = response.choices[0].message.content.strip()
        lines = [line for line in full_text.split('\n') if line.strip()]
        
        title = lines[0].replace('**', '').replace('#', '').strip()
        # الكلمات الدلالية للصورة موجودة في آخر سطر
        img_keywords = lines[-1].strip().lower().replace(" ", "")
        # جسم المقال هو كل شيء بين العنوان والكلمات الدلالية
        raw_body = "\n".join(lines[1:-1]).strip()
        
        body = format_content(raw_body)
        slug = f"article-{random.randint(100000, 999999)}.html"
        
        # تحسين الرابط: إضافة bodybuilding,gym ككلمات أساسية ثابتة لضمان عدم خروج النتائج عن سياق الرياضة
        img = f"https://loremflickr.com/1200/800/bodybuilding,gym,{img_keywords}/all?lock={random.randint(1,99999)}"
        
        full_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}}</style></head><body class="bg-slate-50"><article class="max-w-5xl mx-auto py-20 px-8 bg-white min-h-screen shadow-2xl rounded-[4rem] my-12 border border-slate-100"><div class="mb-12 text-center leading-relaxed"><span class="text-blue-600 font-black tracking-widest uppercase text-sm">{cat} • MAGAZINE</span><h1 class="text-5xl md:text-7xl font-black mt-6 mb-10 text-slate-900 leading-[1.1] text-right">{title}</h1><div class="w-32 h-2 bg-blue-600 mb-12 mr-0 ml-auto rounded-full"></div></div><img src="{img}" class="w-full h-[600px] object-cover rounded-[4rem] mb-16 shadow-2xl ring-1 ring-slate-200"><div class="content max-w-3xl mx-auto text-right">{body}</div><div class="mt-20 p-16 bg-slate-900 rounded-[4rem] text-center text-white"><h4 class="text-3xl font-black mb-6 italic">TDEE ARABIA 🔥</h4><p class="text-slate-400 mb-10 text-xl font-medium">دليلك اليومي لتغيير حياتك للأفضل</p><a href="{DOMAIN}/blog.html" class="inline-block bg-blue-600 px-12 py-5 rounded-3xl font-black hover:bg-blue-700 transition-all text-xl">العودة للمجلة</a></div></article><footer class="text-center py-20 text-slate-400 font-bold uppercase tracking-widest text-xs">© TDEE ARABIA MAGAZINE - PREMIUM CONTENT</footer></body></html>'''
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img, cat)
        update_sitemap(slug)
        print(f"🚀 Published: {slug} | Title: {title} | Image Tags: {img_keywords}")
        
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
