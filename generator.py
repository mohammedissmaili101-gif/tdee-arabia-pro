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

def trigger_vercel_deploy():
    if VERCEL_HOOK:
        try:
            requests.post(VERCEL_HOOK)
            print("🚀 Vercel Deployment Started!")
        except Exception as e: print(f"⚠️ Hook Error: {e}")

def get_gym_image(category):
    # صور احترافية متنوعة (بدون تكرار بفضل الـ lock)
    keywords = {"تنشيف": "fitness", "تضخيم": "bodybuilding", "تغذية": "healthy-food", "مكملات": "protein"}
    kw = keywords.get(category, "gym")
    return f"https://loremflickr.com/1200/800/{kw}/all?lock={random.randint(1, 99999)}"

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    # الماركر هو "Marker" (بمعنى علامة) وليس "Maker"
    marker = ''
    
    new_card = f"""
    <div class="blog-card bg-white rounded-3xl shadow-xl overflow-hidden" data-category="{category}">
        <img src="{image_url}" class="w-full h-64 object-cover" alt="{title}">
        <div class="p-8 text-right">
            <h3 class="text-2xl font-black mb-6">{title}</h3>
            <a href="./{file_slug}" class="bg-blue-600 text-white px-6 py-3 rounded-xl inline-block">اقرأ المقال</a>
        </div>
    </div>"""

    if not os.path.exists(blog_file):
        # إنشاء ملف جديد إذا لم يكن موجوداً
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(f'<!DOCTYPE html><html lang="ar" dir="rtl"><body><div id="blog-grid">{marker}</div></body></html>')

    with open(blog_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if marker in content:
        updated = content.replace(marker, f"{marker}\n{new_card}")
    else:
        # نظام طوارئ في حالة اختفاء الماركر
        updated = content.replace('id="blog-grid">', f'id="blog-grid">\n{marker}\n{new_card}')
        
    with open(blog_file, "w", encoding="utf-8") as f:
        f.write(updated)

def generate_post():
    topics = ["أفضل تمارين الصدر", "كيفية حساب السعرات الحرارية", "أخطاء التنشيف الشائعة"]
    title = random.choice(topics) + " - 2026"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO رياضي بالعربية عن {title}. استعمل HTML tags للفقرات والعناوين."}],
            model="llama-3.3-70b-versatile"
        )
        body = response.choices[0].message.content
        slug = f"post-{random.randint(1000, 9999)}.html"
        img = get_gym_image("تنشيف")
        
        # 1. كريي ملف المقال
        with open(slug, "w", encoding="utf-8") as f:
            f.write(f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"></head><body class="p-10 text-right"><h1>{title}</h1><img src="{img}" style="width:100%">{body}</body></html>')
        
        # 2. حطو في القائمة
        update_blog_list(slug, title, img, "تنشيف")
        
        # 3. إشارة لـ Vercel
        trigger_vercel_deploy()
        
        print(f"✅ تم إنشاء: {slug}")
        print("⚠️ تنبيه: لازم دير Git Push لهاد الملفات لـ GitHub باش Vercel يشوفهم!")
        
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
