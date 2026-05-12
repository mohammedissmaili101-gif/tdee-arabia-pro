import os
import re
import json
import random
import datetime
import requests
from pathlib import Path
from groq import Groq

# =========================================================
# CONFIG
# =========================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

if not GROQ_API_KEY:
    raise Exception("❌ GROQ_API_KEY NOT FOUND")

client = Groq(api_key=GROQ_API_KEY)

DOMAIN = "https://tdee-arabia.vercel.app"

BASE_DIR = Path(__file__).parent

BLOG_FILE = BASE_DIR / "blog.html"
POSTS_DB = BASE_DIR / "posts.json"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"

# =========================================================
# PROFESSIONAL IMAGES
# =========================================================

IMAGES = [
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48",
    "https://images.unsplash.com/photo-1518611012118-696072aa579a",
    "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
    "https://images.unsplash.com/photo-1517963879433-6ad2b056d712",
    "https://images.unsplash.com/photo-1517838277536-f5f99be501cd",
    "https://images.unsplash.com/photo-1519505907962-0a6cb0167c73",
]

# =========================================================
# TOPICS
# =========================================================

TOPICS = {
    "تنشيف": [
        "أفضل نظام تنشيف",
        "أسرار حرق الدهون",
        "كيف تخسر الكرش بسرعة",
        "أفضل أكل للتنشيف",
        "تمارين حرق الدهون"
    ],

    "تضخيم": [
        "أفضل نظام تضخيم",
        "زيادة الكتلة العضلية",
        "أفضل تمارين التضخيم",
        "بناء العضلات بسرعة",
        "أفضل مكملات التضخيم"
    ],

    "تغذية": [
        "أفضل نظام غذائي رياضي",
        "فوائد البروتين للعضلات",
        "التغذية الصحية للرياضيين",
        "أفضل وجبة بعد التمرين",
        "كيفية حساب السعرات"
    ],

    "تمارين": [
        "أفضل تمارين الصدر",
        "أفضل تمارين الأرجل",
        "تمارين الظهر الصحيحة",
        "أفضل جدول تدريبي",
        "كيفية تمرين الكتف"
    ]
}

# =========================================================
# STYLES
# =========================================================

PARAGRAPH_STYLES = [
    "background:#ffffff;border-right:10px solid #2563eb;color:#0f172a;",
    "background:#eff6ff;border-right:10px solid #3b82f6;color:#1e3a8a;",
    "background:#f0fdf4;border-right:10px solid #22c55e;color:#14532d;",
    "background:#fff7ed;border-right:10px solid #f97316;color:#9a3412;",
    "background:#faf5ff;border-right:10px solid #9333ea;color:#581c87;"
]

# =========================================================
# DATABASE
# =========================================================

def load_posts():

    if not POSTS_DB.exists():
        return []

    try:
        with open(POSTS_DB, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return []


def save_post(post):

    posts = load_posts()

    # منع التكرار
    for p in posts:

        if p["slug"] == post["slug"]:
            print("⚠️ المقال موجود مسبقاً")
            return False

    posts.insert(0, post)

    with open(POSTS_DB, "w", encoding="utf-8") as f:

        json.dump(
            posts,
            f,
            ensure_ascii=False,
            indent=4
        )

    return True


# =========================================================
# SLUG
# =========================================================

def generate_slug(title):

    slug = title.lower().strip()

    slug = re.sub(r"\s+", "-", slug)

    slug = re.sub(
        r"[^\u0600-\u06FFa-zA-Z0-9\-]",
        "",
        slug
    )

    return slug + ".html"


# =========================================================
# UNIQUE TITLE
# =========================================================

def generate_unique_title():

    posts = load_posts()

    used_titles = [
        p["title"] for p in posts
    ]

    available = []

    for category, items in TOPICS.items():

        for item in items:

            title = item + " 2026"

            if title not in used_titles:

                available.append(
                    (category, title)
                )

    if not available:
        raise Exception("❌ جميع المواضيع استعملت")

    return random.choice(available)


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = text.replace("##", "")
    text = text.replace("###", "")
    text = text.replace("*", "")
    text = text.strip()

    return text


# =========================================================
# FORMAT ARTICLE
# =========================================================

def format_article(text):

    text = clean_text(text)

    paragraphs = text.split("\n")

    html = ""

    for p in paragraphs:

        p = p.strip()

        if not p:
            continue

        # عنوان
        if (
            len(p) < 80
            and (
                ":" in p
                or "فوائد" in p
                or "نصائح" in p
                or "تمارين" in p
                or "خاتمة" in p
                or "أهمية" in p
            )
        ):

            html += f"""
            <h2 style="
            font-size:42px;
            font-weight:900;
            margin-top:70px;
            margin-bottom:35px;
            padding:25px;
            border-right:12px solid #2563eb;
            background:white;
            border-radius:30px;
            color:#0f172a;
            line-height:1.8;
            box-shadow:0 10px 25px rgba(0,0,0,.05);
            ">
            {p}
            </h2>
            """

        else:

            style = random.choice(PARAGRAPH_STYLES)

            html += f"""
            <div style="
            {style}
            padding:40px;
            border-radius:35px;
            margin-bottom:35px;
            line-height:2.4;
            font-size:24px;
            font-weight:600;
            box-shadow:0 10px 25px rgba(0,0,0,.05);
            ">
            {p}
            </div>
            """

    return html


# =========================================================
# GENERATE ARTICLE
# =========================================================

def generate_article(title, category):

    prompt = f"""

اكتب مقال عربي احترافي طويل جدا عن:

{title}

التصنيف:
{category}

الشروط:

- 2500 كلمة
- SEO قوي
- أسلوب بشري احترافي
- بدون تكرار
- معلومات دقيقة
- عناوين فرعية
- مقدمة قوية
- خاتمة قوية
- لا تستعمل markdown
- لا تستعمل النجوم
- لا تستعمل الرموز

"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.9,
        max_tokens=6000
    )

    return response.choices[0].message.content


# =========================================================
# CREATE POST PAGE
# =========================================================

def create_post_page(
    title,
    category,
    article_html,
    image,
    slug
):

    today = datetime.date.today().strftime("%Y-%m-%d")

    html = f"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>

<meta
name="description"
content="{title} - أفضل المقالات الرياضية"
>

<link
rel="canonical"
href="{DOMAIN}/{slug}"
>

<meta property="og:title" content="{title}">
<meta property="og:image" content="{image}">
<meta property="og:type" content="article">

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

*{{
margin:0;
padding:0;
box-sizing:border-box;
}}

body{{
font-family:'Cairo',sans-serif;
background:#f1f5f9;
}}

.header{{
background:white;
padding:25px;
box-shadow:0 5px 20px rgba(0,0,0,.05);
position:sticky;
top:0;
z-index:999;
}}

.logo{{
font-size:42px;
font-weight:900;
color:#2563eb;
text-decoration:none;
}}

.container{{
max-width:1100px;
margin:auto;
padding:50px 20px;
}}

.hero-image{{
width:100%;
height:500px;
object-fit:cover;
border-radius:40px;
margin-bottom:40px;
box-shadow:0 15px 40px rgba(0,0,0,.12);
}}

.category{{
display:inline-block;
background:#2563eb;
color:white;
padding:12px 25px;
border-radius:18px;
font-weight:900;
font-size:20px;
margin-bottom:25px;
}}

.title{{
font-size:58px;
font-weight:900;
line-height:1.7;
color:#0f172a;
margin-bottom:30px;
}}

.date{{
font-size:22px;
font-weight:700;
color:#64748b;
margin-bottom:50px;
}}

@media(max-width:768px){{

.title{{
font-size:38px;
}}

.hero-image{{
height:300px;
}}

}}

</style>

</head>

<body>

<div class="header">

<a href="./blog.html" class="logo">
TDEE ARABIA 🔥
</a>

</div>

<div class="container">

<img
src="{image}"
class="hero-image"
alt="{title}"
>

<div class="category">
{category}
</div>

<h1 class="title">
{title}
</h1>

<div class="date">
📅 {today}
</div>

{article_html}

</div>

</body>

</html>
"""

    with open(
        BASE_DIR / slug,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print(f"✅ Post Created: {slug}")


# =========================================================
# GENERATE BLOG PAGE
# =========================================================

def generate_blog_page():

    posts = load_posts()

    cards = ""

    for post in posts:

        cards += f"""

<div
class="card"
data-category="{post['category']}"
>

<img
src="{post['image']}"
class="card-image"
alt="{post['title']}"
>

<div class="card-content">

<div class="card-category">
{post['category']}
</div>

<h2 class="card-title">
{post['title']}
</h2>

<div class="card-date">
📅 {post['date']}
</div>

<a
href="./{post['slug']}"
class="read-btn"
>
إقرأ المقال →
</a>

</div>

</div>

"""

    html = f"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TDEE Arabia</title>

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

*{{
margin:0;
padding:0;
box-sizing:border-box;
}}

body{{
font-family:'Cairo',sans-serif;
background:#f1f5f9;
padding:20px;
}}

.container{{
max-width:1450px;
margin:auto;
}}

.logo{{
font-size:55px;
font-weight:900;
color:#2563eb;
margin-bottom:40px;
}}

.search{{
width:100%;
padding:22px;
border:none;
border-radius:25px;
font-size:22px;
margin-bottom:30px;
box-shadow:0 5px 20px rgba(0,0,0,.05);
}}

.filters{{
display:flex;
gap:15px;
flex-wrap:wrap;
margin-bottom:40px;
}}

.filter-btn{{
border:none;
padding:14px 28px;
border-radius:18px;
font-size:18px;
font-weight:900;
cursor:pointer;
background:#0f172a;
color:white;
}}

.grid{{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(340px,1fr));
gap:35px;
}}

.card{{
background:white;
border-radius:35px;
overflow:hidden;
box-shadow:0 10px 30px rgba(0,0,0,.08);
transition:.3s;
}}

.card:hover{{
transform:translateY(-10px);
}}

.card-image{{
width:100%;
height:270px;
object-fit:cover;
}}

.card-content{{
padding:30px;
}}

.card-category{{
display:inline-block;
background:#2563eb;
color:white;
padding:10px 18px;
border-radius:14px;
font-weight:900;
margin-bottom:20px;
}}

.card-title{{
font-size:32px;
line-height:1.7;
font-weight:900;
color:#0f172a;
margin-bottom:20px;
}}

.card-date{{
color:#64748b;
font-weight:700;
margin-bottom:25px;
}}

.read-btn{{
display:block;
text-align:center;
background:#0f172a;
color:white;
padding:18px;
border-radius:18px;
text-decoration:none;
font-weight:900;
font-size:20px;
}}

@media(max-width:768px){{

.logo{{
font-size:38px;
}}

.card-title{{
font-size:26px;
}}

body{{
padding:12px;
}}

}}

</style>

</head>

<body>

<div class="container">

<h1 class="logo">
TDEE ARABIA 🔥
</h1>

<input
type="text"
id="searchInput"
placeholder="ابحث عن مقال..."
class="search"
>

<div class="filters">

<button class="filter-btn" onclick="filterPosts('all')">
الكل
</button>

<button class="filter-btn" onclick="filterPosts('تنشيف')">
تنشيف
</button>

<button class="filter-btn" onclick="filterPosts('تضخيم')">
تضخيم
</button>

<button class="filter-btn" onclick="filterPosts('تغذية')">
تغذية
</button>

<button class="filter-btn" onclick="filterPosts('تمارين')">
تمارين
</button>

</div>

<div class="grid">

{cards}

</div>

</div>

<script>

const searchInput =
document.getElementById("searchInput")

searchInput.addEventListener("keyup",function(){{

const value=this.value.toLowerCase()

document.querySelectorAll(".card")
.forEach(card=>{{

const title=
card.querySelector(".card-title")
.innerText
.toLowerCase()

if(title.includes(value)){{
card.style.display="block"
}}else{{
card.style.display="none"
}}

}})

}})

function filterPosts(category){{

document.querySelectorAll(".card")
.forEach(card=>{{

if(
category==="all"
||
card.dataset.category===category
){{
card.style.display="block"
}}else{{
card.style.display="none"
}}

}})

}}

</script>

</body>

</html>
"""

    with open(
        BLOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print("✅ Blog Updated")


# =========================================================
# SITEMAP
# =========================================================

def update_sitemap():

    posts = load_posts()

    today = datetime.date.today().strftime("%Y-%m-%d")

    urls = ""

    for post in posts:

        urls += f"""

<url>
<loc>{DOMAIN}/{post['slug']}</loc>
<lastmod>{today}</lastmod>
</url>

"""

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

<url>
<loc>{DOMAIN}</loc>
<lastmod>{today}</lastmod>
</url>

{urls}

</urlset>
"""

    with open(
        SITEMAP_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(sitemap)

    print("✅ Sitemap Updated")


# =========================================================
# DEPLOY
# =========================================================

def deploy():

    if not VERCEL_HOOK:
        print("⚠️ No Vercel Hook")
        return

    try:

        requests.post(
            VERCEL_HOOK,
            timeout=10
        )

        print("🚀 Deployment Started")

    except Exception as e:

        print(f"⚠️ Deploy Error: {e}")


# =========================================================
# MAIN
# =========================================================

def generate_post():

    try:

        category, title = generate_unique_title()

        print(f"🚀 Generating: {title}")

        article = generate_article(
            title,
            category
        )

        formatted_article = format_article(
            article
        )

        slug = generate_slug(title)

        image = random.choice(IMAGES)

        create_post_page(
            title,
            category,
            formatted_article,
            image,
            slug
        )

        success = save_post({

            "title": title,
            "slug": slug,
            "image": image,
            "category": category,
            "date": datetime.date.today().strftime("%Y-%m-%d")

        })

        if success:

            generate_blog_page()

            update_sitemap()

            deploy()

            print("🎉 DONE SUCCESSFULLY")

    except Exception as e:

        print(f"❌ ERROR: {e}")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    generate_post()
