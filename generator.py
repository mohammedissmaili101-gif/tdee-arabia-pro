import os
import random
import datetime
from groq import Groq

# 1. إعداد العميل (كيقرا الـ Key من GitHub Secrets)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. بيانات لتوليد آلاف الاحتمالات (pSEO)
weights = [60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110]
goals = [
    {"name": "تنشيف الدهون", "slug": "cutting"},
    {"name": "تضخيم العضلات", "slug": "bulking"},
    {"name": "المحافظة على الوزن", "slug": "maintenance"}
]

def update_sitemap(new_file):
    """تحديث ملف sitemap.xml أوتوماتيكياً"""
    sitemap_path = "sitemap.xml"
    base_url = "https://tdee-arabia.vercel.app/"
    new_url = f"{base_url}{new_file}"
    today = datetime.date.today().isoformat()

    if not os.path.exists(sitemap_path):
        # إنشاء ملف سيت ماب جديد إذا لم يكن موجوداً
        content = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>{base_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>1.0</priority>\n  </url>\n</urlset>'
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)

    with open(sitemap_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # إضافة الرابط الجديد قبل إغلاق </urlset>
    new_entry = f'  <url>\n    <loc>{new_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
    
    # التأكد من أن الرابط غير موجود مسبقاً
    if new_url not in "".join(lines):
        lines.insert(-1, new_entry)
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

def generate_article():
    weight = random.choice(weights)
    goal = random.choice(goals)
    today = datetime.date.today().isoformat()
    
    # الطلب الموجه لـ AI
    prompt = f"""
    اكتب مقال SEO احترافي باللغة العربية.
    العنوان: دليل {goal['name']} الشامل لوزن {weight} كيلوجرام لعام 2026.
    المحتوى يجب أن يتضمن:
    1. مقدمة قوية عن أهمية حساب TDEE.
    2. نصائح دقيقة للتغذية والتمارين لهدف {goal['name']}.
    3. جدول وجبات مقترح يحتوي على بروتين كافٍ.
    4. دعوة للقارئ لاستخدام حاسبة TDEE Arabia في صفحتنا الرئيسية.
    استخدم كلمات مفتاحية: (تنشيف، تضخيم، بروتين، سعرات حرارية، كمال أجسام).
    اللغة: عربية فصحى بسيطة مع لمسة لهجة مغربية خفيفة في النصائح الجانبية.
    """

    # الاتصال بـ Groq API
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )

    article_content = completion.choices[0].message.content
    file_slug = f"guide-{goal['slug']}-{weight}kg-{random.randint(100,999)}.html"

    # تصميم قالب المقال (HTML) باش يجي مع السيت
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دليل {goal['name']} لوزن {weight} كجم | TDEE Arabia</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Cairo', sans-serif; background: #f8fafc; }}</style>
    </head>
    <body class="p-6 md:p-12">
        <div class="max-w-3xl mx-auto bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
            <a href="/" class="text-blue-600 font-bold">← العودة للحاسبة</a>
            <div class="prose prose-slate mt-6 font-bold leading-relaxed">
                {article_content.replace('\n', '<br>')}
            </div>
            <div class="mt-10 p-6 bg-blue-50 rounded-xl text-center">
                <p class="font-black text-blue-800">هل تريد حساب سعراتك بدقة؟</p>
                <a href="/" class="inline-block mt-4 bg-blue-600 text-white px-8 py-3 rounded-full font-black">جرب الحاسبة الآن 🔥</a>
            </div>
        </div>
    </footer>
    </body>
    </html>
    """

    # حفظ الملف
    with open(file_slug, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    # تحديث Sitemap
    update_sitemap(file_slug)
    print(f"✅ تم إنشاء المقال: {file_slug}")

if __name__ == "__main__":
    generate_article()
