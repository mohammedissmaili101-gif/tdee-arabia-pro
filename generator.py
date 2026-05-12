import os
import random
import datetime
import re
import requests
from pathlib import Path
from groq import Groq

# ======================================================
# CONFIG
# ======================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

DOMAIN = "https://tdee-arabia.vercel.app"

BASE_DIR = Path(__file__).parent

BLOG_FILE = BASE_DIR / "blog.html"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"

# ======================================================
# STYLES
# ======================================================

paragraph_styles = [
    "bg-white border-r-4 border-blue-500 text-slate-800",
    "bg-blue-50 border-r-4 border-indigo-400 text-indigo-900",
    "bg-slate-50 border-r-4 border-slate-400 text-slate-900",
    "bg-emerald-50 border-r-4 border-emerald-400 text-emerald-900"
]

# ======================================================
# TOPICS
# ======================================================

topics = {
    "تنشيف": [
        "أسرار حرق الدهون",
        "أفضل نظام تنشيف",
        "كيف تخسر الدهون بسرعة",
        "أفضل أكل للتنشيف",
        "أقوى تمارين الكارديو"
    ],
    "تضخيم": [
        "أقوى نظام تضخيم",
        "زيادة الكتلة العضلية",
        "أفضل تمارين التضخيم",
        "خطة بناء العضلات",
        "أفضل مكملات التضخيم"
    ],
    "تغذية": [
        "أفضل نظام غذائي رياضي",
        "أهمية البروتين للعضلات",
        "التغذية الصحية للرياضيين",
        "كيف تحسب سعراتك الحرارية"
    ]
}

# ======================================================
# UTILITIES
# ======================================================

def trigger_vercel_deploy():
    if not VERCEL_HOOK:
        print("⚠️ No Vercel Hook Found")
        return

    try:
        response = requests.post(VERCEL_HOOK, timeout=10)

        if response.status_code in [200, 201]:
            print("🚀 Vercel Deployment Started!")
        else:
            print(f"⚠️ Deploy Error: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Deployment Hook Error: {e}")


def clean_text(text):
    text = text.strip()

    # إزالة markdown الزائد
    text = text.replace("##", "")
    text = text.replace("###", "")
    text = text.replace("*", "")

    return text


def generate_slug(title):
    slug = title.strip()

    slug = re.sub(r"\s+", "-", slug)

    slug = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\-]", "", slug)

    return slug + ".html"


# ======================================================
# CONTENT FORMATTER
# ======================================================

def format_content(text):
    text = clean_text(text)

    paragraphs = text.split("\n")

    formatted_html = ""

    for p in paragraphs:

        p = p.strip()

        if not p:
            continue

        # عنوان
        if len(p) < 80 and (
            p.endswith(":")
            or "فوائد" in p
            or "نصائح" in p
            or "تمارين" in p
            or "خاتمة" in p
        ):

            formatted_html += f"""
            <h2 class="text-3xl font-black text-slate-800 mt-12 mb-6 border-r-8 border-blue-600 pr-4 bg-slate-100 py-4 rounded-l-2xl shadow-sm text-right">
                {p}
            </h2>
            """

        else:

            style = random.choice(paragraph_styles)

            formatted_html += f"""
            <div class="p-8 rounded-[2.5rem] border {style} shadow-sm leading-[2.6rem] text-xl mb-8 font-medium text-right">
                {p}
            </div>
            """

    return formatted_html


# ======================================================
# SITEMAP
# ======================================================

def update_sitemap(file_slug):

    url = f"{DOMAIN}/{file_slug}"

    today = datetime.date.today().strftime("%Y-%m-%d")

    if not SITEMAP_FILE.exists():

        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

<url>
<loc>{DOMAIN}/</loc>
<lastmod>{today}</lastmod>
</url>

</urlset>
"""

        SITEMAP_FILE.write_text(sitemap_content, encoding="utf-8")

    content = SITEMAP_FILE.read_text(encoding="utf-8")

    if url in content:
        return

    new_url = f"""
<url>
<loc>{url}</loc>
<lastmod>{today}</lastmod>
</url>

</urlset>
"""

    updated = content.replace("</urlset>", new_url)

    SITEMAP_FILE.write_text(updated, encoding="utf-8")

    print("✅ Sitemap Updated")


# ======================================================
# BLOG PAGE
# ======================================================

def update_blog_list(file_slug, title, image_url, category):

    today = datetime.date.today().strftime("%Y-%m-%d")

    marker = "PLACEHOLDER_MARKER"

    new_card = f"""
    
    <div class="blog-card bg-white rounded-[3rem] shadow-xl overflow-hidden group mb-10" data-category="{category}">
        
        <img src="{image_url}" class="w-full h-72 object-cover" alt="{title}">

        <div class="p-10 text-right">

            <span class="text-blue-500 font-bold">
                {today}
            </span>

            <h3 class="post-title text-2xl font-black mt-4 mb-8 text-slate-900">
                {title}
            </h3>

            <a href="./{file_slug}"
               class="inline-block w-full text-center bg-slate-900 text-white font-black py-5 rounded-2xl hover:bg-blue-600 transition-all shadow-lg">

               إقرأ التفاصيل ←

            </a>

        </div>

    </div>
    """

    # إنشاء blog page إذا غير موجودة
    if not BLOG_FILE.exists():

        initial_html = f"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TDEE Arabia Blog</title>

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

body {{
    font-family: 'Cairo', sans-serif;
}}

</style>

</head>

<body class="bg-slate-50">

<nav class="bg-white p-6 shadow-sm sticky top-0 z-50 border-b">

<div class="max-w-7xl mx-auto flex justify-between items-center">

<h1 class="text-3xl font-black text-blue-600">
TDEE ARABIA 🔥
</h1>

</div>

</nav>

<main class="max-w-7xl mx-auto px-6 py-16 text-right">

<div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">

{marker}

{new_card}

</div>

</main>

</body>

</html>
"""

        BLOG_FILE.write_text(initial_html, encoding="utf-8")

        print("✅ Blog Page Created")

    else:

        content = BLOG_FILE.read_text(encoding="utf-8")

        if file_slug in content:
            print("⚠️ Post already exists")
            return

        if marker in content:

            updated = content.replace(
                marker,
                f"{marker}\n{new_card}"
            )

        else:

            updated = content.replace(
                'id="blog-grid"',
                f'id="blog-grid">\n{marker}\n{new_card}'
            )

        BLOG_FILE.write_text(updated, encoding="utf-8")

        print("✅ Blog Updated")


# ======================================================
# AI ARTICLE GENERATION
# ======================================================

def generate_article(title):

    prompt = f"""
اكتب مقال عربي احترافي SEO طويل جدا عن:

{title}

الشروط:

- أكثر من 1500 كلمة
- أسلوب بشري احترافي
- معلومات دقيقة
- بدون تكرار
- فقرات طويلة
- مقدمة قوية
- خاتمة قوية
- عناوين فرعية واضحة
- مناسب لمحركات البحث
- لا تستعمل markdown
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.8,
        max_tokens=4000
    )

    return response.choices[0].message.content


# ======================================================
# CREATE POST PAGE
# ======================================================

def create_post_page(title, body, image_url, slug):

    today = datetime.date.today().strftime("%Y-%m-%d")

    full_html = f"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>

<meta name="description"
      content="{title} - أفضل المقالات الرياضية والتغذية في TDEE Arabia">

<meta name="keywords"
      content="رياضة, تضخيم, تنشيف, كمال أجسام, تغذية">

<link rel="canonical" href="{DOMAIN}/{slug}">

<meta property="og:title" content="{title}">
<meta property="og:description" content="مقال احترافي عن {title}">
<meta property="og:image" content="{image_url}">
<meta property="og:type" content="article">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

body {{
    font-family: 'Cairo', sans-serif;
    background: #f8fafc;
}}

</style>

</head>

<body>

<nav class="bg-white shadow-sm border-b sticky top-0 z-50">

<div class="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">

<h1 class="text-3xl font-black text-blue-600">
TDEE ARABIA 🔥
</h1>

</div>

</nav>

<main class="max-w-4xl mx-auto px-6 py-16">

<img src="{image_url}"
     class="w-full rounded-[3rem] shadow-2xl mb-12 object-cover max-h-[500px]"
     alt="{title}">

<h1 class="text-5xl font-black text-slate-900 mb-10 leading-tight text-right">
{title}
</h1>

<div class="text-right text-slate-500 font-bold mb-12">
📅 {today}
</div>

{body}

</main>

</body>

</html>
"""

    post_path = BASE_DIR / slug

    post_path.write_text(full_html, encoding="utf-8")

    print(f"✅ Post Created: {slug}")


# ======================================================
# MAIN GENERATOR
# ======================================================

def generate_post():

    category = random.choice(list(topics.keys()))

    title = random.choice(topics[category]) + " 2026"

    print(f"🚀 Generating: {title}")

    try:

        article = generate_article(title)

        formatted_body = format_content(article)

        slug = generate_slug(title)

        image_url = f"https://loremflickr.com/1200/800/gym?lock={random.randint(1,99999)}"

        create_post_page(
            title=title,
            body=formatted_body,
            image_url=image_url,
            slug=slug
        )

        update_blog_list(
            file_slug=slug,
            title=title,
            image_url=image_url,
            category=category
        )

        update_sitemap(slug)

        trigger_vercel_deploy()

        print("🎉 ALL DONE SUCCESSFULLY")

    except Exception as e:

        print(f"❌ ERROR: {e}")


# ======================================================
# START
# ======================================================

if __name__ == "__main__":
    generate_post()
