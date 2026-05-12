import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# صور عالية الجودة
gym_images = [
    "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/949126/pexels-photo-949126.jpeg?auto=compress&cs=tinysrgb&w=800"
]

def update_blog_list(file_slug, title, image_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # قالب بطاقة المقال
    new_card = f"""
    <div class="bg-white rounded-3xl shadow-xl overflow-hidden hover:scale-105 transition-all duration-500 border border-slate-100 group">
        <div class="relative overflow-hidden">
            <img src="{image_url}" class="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-500" onerror="this.src='https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=800'">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">جديد</div>
        </div>
        <div class="p-6">
            <span class="text-blue-500 font-bold text-sm">{today}</span>
            <h3 class="text-2xl font-black mt-3 mb-5 text-slate-900 leading-snug h-20 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-bold py-4 rounded-2xl hover:bg-slate-900 transition-all">اقرأ المقال</a>
        </div>
    </div>
    """

    if not os.path.exists(blog_file):
        # إنشاء الملف لأول مرة مع "العلامة السرية"
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head><body class="bg-slate-50 font-['Cairo'] text-right"><nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm p-6"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="bg-slate-100 px-6 py-2 rounded-full font-bold text-slate-600">الرئيسية</a></div></nav><main class="max-w-6xl mx-auto px-4 mt-12"><h2 class="text-5xl font-black mb-12 text-slate-900">آخر المقالات</h2><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-24">
        {new_card}
        </div></main></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        # البحث عن العلامة السرية وزيادة المقال فوقها
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        marker = ''
        if marker in content:
            new_content = content.replace(marker, new_card, 1) # تعويض العلامة بالمقال الجديد + علامة جديدة
            with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    topics = ["تنشيف الكرش", "تضخيم العضلات", "أفضل مكمل بروتين", "أخطاء التمرين", "خطة غذائية"]
    title = f"{random.choice(topics)} لوزن {random.randint(60, 110)} كجم"
    image = random.choice(gym_images)
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\n', '<br>')
        file_slug = f"post-{random.randint(10000, 99999)}.html"

        article_html = f"""
        <!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head>
        <body class="bg-slate-50 font-['Cairo'] text-right"><nav class="bg-white p-4 border-b"><div class="max-w-4xl mx-auto"><a href="/blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a></div></nav>
        <main class="max-w-4xl mx-auto my-12 px-4"><img src="{image}" class="w-full h-96 object-cover rounded-[3rem] shadow-2xl mb-12"><article class="bg-white p-10 rounded-[3rem] shadow-sm">
        <h1 class="text-4xl font-black mb-8 text-slate-900">{title}</h1><div class="text-xl leading-relaxed text-slate-700">{body}</div></article></main></body></html>
        """
        
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        update_blog_list(file_slug, title, image)
        print(f"✅ Success: {file_slug}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate()
