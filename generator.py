import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOMAIN = "https://tdee-arabia.vercel.app"
gym_images = [
    "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/949126/pexels-photo-949126.jpeg?auto=compress&cs=tinysrgb&w=800"
]

def update_blog_list(file_slug, title, image_url, category):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # قالب البطاقة مع "Category" للبحث والتصفية
    new_card = f"""
    <div class="blog-card bg-white rounded-3xl shadow-xl overflow-hidden hover:scale-105 transition-all duration-500 border border-slate-100 group" data-category="{category}">
        <div class="relative overflow-hidden">
            <img src="{image_url}" class="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-500">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">{category}</div>
        </div>
        <div class="p-6">
            <h3 class="post-title text-2xl font-black mb-5 text-slate-900 leading-snug h-20 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-bold py-4 rounded-2xl hover:bg-slate-900 transition-all">اقرأ الآن</a>
        </div>
    </div>
    """

    if not os.path.exists(blog_file):
        # إنشاء الملف مع خانة البحث والسكربت
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
        <style>.hidden {{ display: none; }}</style></head>
        <body class="bg-slate-50 font-['Cairo'] text-right">
            <nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm p-6"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="font-bold text-slate-600">الرئيسية</a></div></nav>
            <main class="max-w-6xl mx-auto px-4 mt-12">
                <div class="text-center mb-16">
                    <h2 class="text-5xl font-black mb-8 text-slate-900">استكشف مقالاتنا</h2>
                    <div class="max-w-2xl mx-auto relative mb-8">
                        <input type="text" id="searchInput" placeholder="ابحث عن موضوع أو وزن معيين..." class="w-full p-5 rounded-2xl border-2 border-slate-200 focus:border-blue-500 outline-none text-xl shadow-lg transition-all">
                    </div>
                    <div class="flex flex-wrap justify-center gap-3 mb-10">
                        <button onclick="filterPosts('الكل')" class="bg-slate-900 text-white px-6 py-2 rounded-full font-bold">الكل</button>
                        <button onclick="filterPosts('تنشيف')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold shadow-sm hover:bg-blue-600 hover:text-white transition-all">تنشيف</button>
                        <button onclick="filterPosts('تضخيم')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold shadow-sm hover:bg-blue-600 hover:text-white transition-all">تضخيم</button>
                        <button onclick="filterPosts('مكملات')" class="bg-white text-slate-600 px-6 py-2 rounded-full font-bold shadow-sm hover:bg-blue-600 hover:text-white transition-all">مكملات</button>
                    </div>
                </div>
                <div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-24">{new_card}</div>
            </main>
            <script>
                // سكربت البحث
                document.getElementById('searchInput').addEventListener('keyup', function(e) {{
                    let term = e.target.value.toLowerCase();
                    let cards = document.querySelectorAll('.blog-card');
                    cards.forEach(card => {{
                        let title = card.querySelector('.post-title').innerText.toLowerCase();
                        card.classList.toggle('hidden', !title.includes(term));
                    }});
                }});
                // سكربت الفلترة
                function filterPosts(cat) {{
                    let cards = document.querySelectorAll('.blog-card');
                    cards.forEach(card => {{
                        if(cat === 'الكل') {{ card.classList.remove('hidden'); }}
                        else {{ card.classList.toggle('hidden', card.getAttribute('data-category') !== cat); }}
                    }});
                }}
            </script>
        </body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        marker = ''
        if marker in content:
            new_content = content.replace(marker, new_card, 1)
            with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    # ربط المواضيع بالتصنيفات
    cats = {
        "تنشيف": ["حرق دهون البطن", "تنشيف الجسم", "كارديو الصباح"],
        "تضخيم": ["بناء عضلات الصدر", "تضخيم العضلات", "تمارين القوة"],
        "مكملات": ["أفضل واي بروتين", "فوائد الكرياتين", "مكملات الطاقة"]
    }
    category = random.choice(list(cats.keys()))
    topic = random.choice(cats[category])
    weight = random.randint(60, 110)
    title = f"{topic} لمن وزنه {weight} كجم"
    image = random.choice(gym_images)
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\n', '<br>')
        file_slug = f"post-{random.randint(10000, 99999)}.html"
        
        # كود المقال (مختصر للتوضيح)
        article_html = f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='UTF-8'><script src='https://cdn.tailwindcss.com'></script></head><body class='bg-slate-50 font-serif p-8'><a href='/blog.html'>العودة</a><h1 class='text-4xl font-black my-8'>{title}</h1><div class='text-xl'>{body}</div></body></html>"
        
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        update_blog_list(file_slug, title, image, category)
        print(f"✅ Success: {title} ({category})")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate()
