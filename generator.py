import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# مكتبة صور رياضية (روابط مباشرة من Unsplash)
gym_images = [
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800",
    "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=800",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
    "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800"
]

weights = [60, 70, 80, 90, 100]
goals = [{"name": "تنشيف الدهون", "slug": "cutting"}, {"name": "تضخيم العضلات", "slug": "bulking"}]

def generate_blog_post():
    weight = random.choice(weights)
    goal = random.choice(goals)
    img_url = random.choice(gym_images)
    title = f"دليل {goal['name']} لوزن {weight} كجم - نصائح 2026"
    
    prompt = f"اكتب مقال SEO احترافي باللغة العربية عن {goal['name']} لشخص وزنه {weight}kg. استعمل تقسيم بفقرات وعناوين فرعية."
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    body = completion.choices[0].message.content.replace('\n', '<br>')
    file_slug = f"post-{random.randint(1000,9999)}.html"

    # قالب صفحة المقال (بحال Blogger)
    post_template = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body class="bg-slate-50 font-['Cairo']">
        <nav class="bg-white shadow-sm p-4 sticky top-0"><div class="max-w-3xl mx-auto flex justify-between items-center"><a href="/blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a><a href="/" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold">جرب الحاسبة 🔥</a></div></nav>
        <article class="max-w-3xl mx-auto my-10 bg-white rounded-3xl shadow-lg overflow-hidden">
            <img src="{img_url}" class="w-full h-64 object-cover">
            <div class="p-8">
                <h1 class="text-3xl font-black mb-6 leading-tight">{title}</h1>
                <div class="text-slate-700 leading-loose font-bold">{body}</div>
            </div>
        </article>
    </body>
    </html>
    """
    
    with open(file_slug, "w", encoding="utf-8") as f:
        f.write(post_template)
    
    update_blog_list(file_slug, title, img_url)

def update_blog_list(file_slug, title, img_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    if not os.path.exists(blog_file):
        initial_content = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head><body class="bg-slate-100 font-['Cairo']"><nav class="p-6 text-center"><a href="/" class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</a><p class="font-bold text-slate-500">مدونة اللياقة والتغذية</p></nav><main class="max-w-5xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6" id="blog-grid"></main></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_content)

    with open(blog_file, "r", encoding="utf-8") as f: content = f.read()

    new_card = f"""
    <div class="bg-white rounded-2xl shadow-md overflow-hidden hover:scale-[1.02] transition-all">
        <img src="{img_url}" class="w-full h-48 object-cover">
        <div class="p-4">
            <span class="text-xs text-blue-600 font-bold">{today}</span>
            <h3 class="text-xl font-bold mt-2 mb-4">{title}</h3>
            <a href="/{file_slug}" class="inline-block bg-blue-50 text-blue-600 px-4 py-2 rounded-lg font-bold text-sm">اقرأ المقال</a>
        </div>
    </div>
    """
    new_content = content.replace('', '\n' + new_card)
    with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

if __name__ == "__main__":
    generate_blog_post()
