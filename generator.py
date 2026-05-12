import os
import random
import datetime
from groq import Groq

# إعداد العميل
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# مكتبة الصور
gym_images = [
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800",
    "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=800",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
    "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800"
]

def update_sitemap(new_file):
    sitemap_path = "sitemap.xml"
    base_url = "https://tdee-arabia.vercel.app/"
    new_url = f"{base_url}{new_file}"
    today = datetime.date.today().isoformat()
    if not os.path.exists(sitemap_path):
        content = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>{base_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>1.0</priority>\n  </url>\n</urlset>'
        with open(sitemap_path, "w", encoding="utf-8") as f: f.write(content)
    with open(sitemap_path, "r", encoding="utf-8") as f: lines = f.readlines()
    if new_url not in "".join(lines):
        lines.insert(-1, f'  <url>\n    <loc>{new_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>\n')
        with open(sitemap_path, "w", encoding="utf-8") as f: f.writelines(lines)

def update_blog_list(file_slug, title, img_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(blog_file):
        initial = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head><body class="bg-slate-100 font-['Cairo']"><nav class="p-6 text-center bg-white shadow-sm"><a href="/" class="text-3xl font-black text-blue-600">TDEE ARABIA 🔥</a><div class="mt-2"><a href="/" class="text-sm font-bold text-slate-500 hover:text-blue-600">العودة للحاسبة</a></div></nav><main class="max-w-5xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="blog-grid"></main></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial)
    with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
    new_card = f"""
    <div class="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-all border border-slate-200">
        <img src="{img_url}" class="w-full h-48 object-cover">
        <div class="p-4">
            <span class="text-xs text-blue-600 font-bold">{today}</span>
            <h3 class="text-xl font-bold mt-2 mb-4 h-14 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="block text-center bg-blue-600 text-white px-4 py-2 rounded-lg font-bold text-sm hover:bg-blue-700">اقرأ المزيد</a>
        </div>
    </div>
    """
    new_content = content.replace('', '\n' + new_card)
    with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    weight = random.choice([60, 70, 80, 90, 100])
    goal = random.choice([{"n": "تنشيف", "s": "cutting"}, {"n": "تضخيم", "s": "bulking"}])
    img = random.choice(gym_images)
    title = f"أفضل نظام غذائي لل{goal['n']} بوزن {weight} كجم لعام 2026"
    
    res = client.chat.completions.create(
        messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}. استخدم فقرات واضحة ونصائح رياضية."}],
        model="llama3-8b-8192",
    )
    body = res.choices[0].message.content.replace('\n', '<br>')
    file_slug = f"post-{random.randint(1000,9999)}.html"

    template = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head>
    <body class="bg-slate-50 font-['Cairo']">
        <nav class="bg-white shadow-sm p-4 sticky top-0 z-50"><div class="max-w-3xl mx-auto flex justify-between items-center"><a href="/blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a><a href="/" class="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold">جرب الحاسبة 🔥</a></div></nav>
        <article class="max-w-3xl mx-auto my-10 bg-white rounded-3xl shadow-lg overflow-hidden border border-slate-100">
            <img src="{img}" class="w-full h-72 object-cover">
            <div class="p-8"><h1 class="text-3xl font-black mb-6 leading-tight text-slate-900">{title}</h1><div class="text-slate-700 leading-loose font-bold">{body}</div></div>
        </article>
    </body></html>
    """
    with open(file_slug, "w", encoding="utf-8") as f: f.write(template)
    update_blog_list(file_slug, title, img)
    update_sitemap(file_slug)
    print(f"Done: {file_slug}")

if __name__ == "__main__":
    generate()
