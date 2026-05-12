import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# صور رياضية
gym_images = [
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800",
    "https://images.unsplash.com/photo-1541534741688-6078c64b5903?w=800"
]

def update_blog_list(file_slug, title, image_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # قالب بطاقة المقال
    new_card = f"""
    <div class="bg-white rounded-3xl shadow-xl overflow-hidden hover:scale-105 transition-transform duration-300 border border-slate-100">
        <img src="{image_url}" class="w-full h-48 object-cover">
        <div class="p-6">
            <span class="text-blue-600 font-bold text-sm">{today}</span>
            <h3 class="text-2xl font-black mt-2 mb-4 text-slate-900 leading-tight">{title}</h3>
            <a href="/{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-bold py-3 rounded-2xl">اقرأ المقال الآن</a>
        </div>
    </div>
    """

    if not os.path.exists(blog_file):
        # إنشاء ملف جديد بالكامل إذا لم يكن موجوداً
        content = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head><body class="bg-slate-50 font-['Cairo'] text-right"><nav class="bg-white shadow-md p-6 mb-10"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="text-slate-600 font-bold">الرئيسية</a></div></nav><main class="max-w-6xl mx-auto px-4"><h2 class="text-4xl font-black mb-12 text-slate-800 border-r-8 border-blue-600 pr-4">آخر المقالات</h2><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-20">{new_card}</div></main></body></html>"""
    else:
        # إذا كان موجوداً، نضيف المقال الجديد في الأعلى
        with open(blog_file, "r", encoding="utf-8") as f:
            content = f.read()
        marker = 'id="blog-grid">'
        content = content.replace(marker, marker + "\n" + new_card)

    with open(blog_file, "w", encoding="utf-8") as f:
        f.write(content)

def generate():
    weight = random.randint(60, 100)
    image = random.choice(gym_images)
    title = f"أفضل خطة غذائية احترافية لوزن {weight} كجم"
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}. اجعله مفصلاً مع نصائح."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\n', '<br>')
        file_slug = f"post-{random.randint(1000, 9999)}.html"

        article_html = f"""
        <!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head>
        <body class="bg-slate-50 font-['Cairo'] text-right"><nav class="bg-white p-4 border-b"><div class="max-w-4xl mx-auto"><a href="/blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a></div></nav>
        <main class="max-w-4xl mx-auto my-12 px-4"><img src="{image}" class="w-full h-96 object-cover rounded-[2.5rem] mb-12"><article class="bg-white p-10 rounded-[2.5rem] shadow-sm">
        <h1 class="text-4xl font-black mb-8 text-slate-900">{title}</h1><div class="text-xl leading-relaxed text-slate-700">{body}</div></article></main></body></html>
        """
        
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        update_blog_list(file_slug, title, image)
        print(f"✅ Success: {file_slug}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate()
