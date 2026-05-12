import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# صور رياضية بجودة عالية
gym_images = [
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800",
    "https://images.unsplash.com/photo-1541534741688-6078c64b5903?w=800"
]

def update_blog_list(file_slug, title, image_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    if not os.path.exists(blog_file):
        initial_html = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>المدونة | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head><body class="bg-slate-50 font-['Cairo'] text-right"><nav class="bg-white shadow-md p-6 mb-10"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600">TDEE ARABIA 🔥</h1><a href="/" class="text-slate-600 font-bold">الرئيسية</a></div></nav><main class="max-w-6xl mx-auto px-4"><h2 class="text-4xl font-black mb-12 text-slate-800 border-r-8 border-blue-600 pr-4">آخر المقالات الحصرية</h2><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-20"></div></main></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    
    with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
    
    new_card = f"""
    <div class="bg-white rounded-3xl shadow-xl overflow-hidden hover:scale-105 transition-transform duration-300 border border-slate-100">
        <img src="{image_url}" class="w-full h-48 object-cover">
        <div class="p-6">
            <span class="text-blue-600 font-bold text-sm tracking-wider">{today}</span>
            <h3 class="text-2xl font-black mt-2 mb-4 text-slate-900 leading-tight h-20 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="inline-block w-full text-center bg-blue-600 text-white font-bold py-3 rounded-2xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200">اقرأ المقال الآن</a>
        </div>
    </div>
    """
    
    if 'id="blog-grid">' in content:
        new_content = content.replace('id="blog-grid">', 'id="blog-grid">' + "\n" + new_card)
        with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    weight = random.randint(60, 100)
    image = random.choice(gym_images)
    title = f"دليلك الشامل للنظام الغذائي المثالي لوزن {weight} كجم"
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي وطويل بالعربية عن {title}. استخدم لغة حماسية، فقرات منظمة، وجداول نصائح."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\\n', '<br>')
        file_slug = f"post-{random.randint(1000, 9999)}.html"

        article_template = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"></head>
        <body class="bg-slate-50 font-['Cairo'] text-right">
            <nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 p-4 border-b border-slate-100"><div class="max-w-4xl mx-auto flex justify-between items-center"><a href="/blog.html" class="text-blue-600 font-bold">← العودة للمدونة</a><span class="font-black text-slate-800">TDEE ARABIA</span></div></nav>
            <main class="max-w-4xl mx-auto my-12 px-4">
                <img src="{image}" class="w-full h-96 object-cover rounded-[2.5rem] shadow-2xl mb-12">
                <article class="bg-white p-10 md:p-16 rounded-[2.5rem] shadow-sm border border-slate-100">
                    <h1 class="text-4xl md:text-5xl font-black mb-8 text-slate-900 leading-tight">{title}</h1>
                    <div class="text-xl leading-relaxed text-slate-700 space-y-6">{body}</div>
                </article>
            </main>
        </body></html>
        """
        
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_template)
        update_blog_list(file_slug, title, image)
        print(f"✅ Success: {file_slug}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate()
