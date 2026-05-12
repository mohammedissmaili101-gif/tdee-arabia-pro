import os
import random
import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def update_blog_list(file_slug, title):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # إيلا ماكانش ملف المدونة، ك نصاوبوه
    if not os.path.exists(blog_file):
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>المدونة</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-100 p-10"><h1 class="text-3xl font-bold text-center mb-10">آخر المقالات</h1><div id="blog-grid" class="grid gap-6"></div></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    
    with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
    
    # زيادة رابط المقال الجديد فـ القائمة
    new_card = f'<div class="bg-white p-6 rounded-xl shadow-sm border"><span class="text-gray-400 text-sm">{today}</span><h2 class="text-xl font-bold">{title}</h2><a href="/{file_slug}" class="text-blue-600 font-bold mt-2 inline-block">اقرأ المقال ←</a></div>'
    
    if 'id="blog-grid">' in content:
        new_content = content.replace('id="blog-grid">', 'id="blog-grid">' + "\n" + new_card)
        with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    weight = random.randint(60, 100)
    title = f"أفضل نظام غذائي بوزن {weight} كجم لعام 2026"
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي بالعربية عن {title}. استخدم عناوين فرعية."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\n', '<br>')
        file_slug = f"post-{random.randint(1000, 9999)}.html"

        article_html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"><title>{title}</title><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-slate-50 p-6 md:p-20 font-sans">
            <article class="max-w-2xl mx-auto bg-white p-8 rounded-3xl shadow-lg">
                <h1 class="text-3xl font-black mb-6">{title}</h1>
                <div class="text-lg leading-relaxed text-gray-700">{body}</div>
                <a href="/blog.html" class="mt-10 block text-blue-600 font-bold">← العودة للمدونة</a>
            </article>
        </body></html>
        """
        
        # حفظ المقال
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        
        # تحديث قائمة المدونة
        update_blog_list(file_slug, title)
        print(f"✅ تم بنجاح: {file_slug}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    generate()
