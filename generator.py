import os
import random
import datetime
import re
from groq import Groq

# الإعدادات
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia-pro.vercel.app"

def format_content(text):
    # تنسيق احترافي للمجلة
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*]', '', text)
    paragraphs = text.split('\n')
    formatted_html = ""
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('**') and p.endswith('**'):
            title = p.replace('**', '')
            formatted_html += f'<h2 class="text-3xl font-black text-slate-800 mt-14 mb-8 border-r-[10px] border-blue-600 pr-5 bg-gradient-to-l from-blue-50 to-transparent py-4 rounded-l-3xl text-right leading-tight">{title}</h2>'
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
                <span>PREMIUM EDITION</span>
            </div>
            <h3 class="text-2xl font-black mb-6 text-slate-900 leading-snug group-hover:text-blue-600 transition-colors">{title}</h3>
            <a href="{full_post_url}" class="inline-flex items-center gap-2 text-blue-600 font-black text-sm uppercase tracking-wider group-hover:gap-4 transition-all underline underline-offset-8">تفاصيل المقال ←</a>
        </div>
    </div>'''
    
    if os.path.exists(blog_file):
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        if marker in content:
            updated = content.replace(marker, f"{marker}\n{new_card}")
            with open(blog_file, "w", encoding="utf-8") as f: f.write(updated)

def generate_post():
    # ربط الأصناف بكلمات مفتاحية محددة للصور
    data_map = {
        "تغذية": {
            "topics": ["أفضل بروتين طبيعي للعضلات", "وجبات ما قبل التمرين للطاقة", "أسرار حرق الدهون في رمضان"],
            "img_keywords": "healthy-food,protein-shake,fitness-meal"
        },
        "تدريب": {
            "topics": ["أقوى تمارين الصدر في البيت", "جدول تدريب 5 أيام للمحترفين", "كيفية تجنب إصابات الظهر"],
            "img_keywords": "gym-workout,bodybuilder-training,heavy-lifting"
        },
        "مكملات": {
            "topics": ["دليل الكرياتين للمبتدئين", "متى يجب تناول الـ BCAA؟", "أفضل حوارق الدهون الطبيعية"],
            "img_keywords": "supplements-fitness,gym-bottle,vitamin-capsules"
        }
    }
    
    cat = random.choice(list(data_map.keys()))
    title = random.choice(data_map[cat]["topics"])
    img_tag = data_map[cat]["img_keywords"]
    
    try:
        # طلب المقال بأسلوب مجلة عالمية
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقالاً طويلاً جداً ومفصلاً لمجلة رياضية فاخرة عن: {title}. استخدم أسلوباً مشوقاً، عناوين فرعية بين **، نصائح عملية، وخاتمة ملهمة. المقال يجب أن يكون موجهاً للشباب العربي الطموح."}],
            model="llama-3.3-70b-versatile"
        )
        
        body = format_content(response.choices[0].message.content)
        slug = f"article-{random.randint(100000, 999999)}.html"
        
        # اختيار صورة دقيقة بناءً على الصنف
        img_url = f"https://loremflickr.com/1280/720/{img_tag}/all?lock={random.randint(1,999)}"
        
        full_html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:"Cairo", sans-serif;}}</style></head><body class="bg-slate-50"><article class="max-w-5xl mx-auto py-20 px-8 bg-white min-h-screen shadow-2xl rounded-[4rem] my-12 border border-slate-100"><div class="mb-12 text-center leading-relaxed"><span class="text-blue-600 font-black tracking-widest uppercase text-sm">{cat} • MAGAZINE</span><h1 class="text-5xl md:text-7xl font-black mt-6 mb-10 text-slate-900 leading-[1.1] text-right">{title}</h1><div class="w-32 h-2 bg-blue-600 mb-12 mr-0 ml-auto rounded-full"></div></div><img src="{img_url}" class="w-full h-[600px] object-cover rounded-[4rem] mb-16 shadow-2xl ring-1 ring-slate-200"><div class="content max-w-3xl mx-auto text-right">{body}</div></article></body></html>'''
        
        with open(slug, "w", encoding="utf-8") as f: f.write(full_html)
        update_blog_list(slug, title, img_url, cat)
        print(f"✅ تم النشر بنجاح: {title}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    generate_post()
