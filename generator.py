import os
import random
import datetime
import re
import requests
import json
from pathlib import Path
from groq import Groq

# =========================================================
# CONFIG
# =========================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VERCEL_HOOK = os.environ.get("VERCEL_DEPLOY_HOOK")

if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

DOMAIN = "https://tdee-arabia.vercel.app"

BASE_DIR = Path(__file__).parent

BLOG_FILE = BASE_DIR / "blog.html"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"
USED_POSTS_FILE = BASE_DIR / "used_posts.json"

# =========================================================
# STYLES
# =========================================================

paragraph_styles = [
    "bg-white border-r-8 border-blue-500 text-slate-800",
    "bg-blue-50 border-r-8 border-indigo-400 text-indigo-900",
    "bg-emerald-50 border-r-8 border-emerald-400 text-emerald-900",
    "bg-orange-50 border-r-8 border-orange-400 text-orange-900",
    "bg-purple-50 border-r-8 border-purple-400 text-purple-900",
]

# =========================================================
# TOPICS
# =========================================================

topics = {
    "تنشيف": [
        "أسرار حرق الدهون",
        "أفضل نظام تنشيف",
        "كيف تخسر الدهون بسرعة",
        "أفضل أكل للتنشيف",
        "أقوى تمارين الكارديو",
        "كيف تنشف جسمك بدون خسارة العضلات",
    ],
    "تضخيم": [
        "أقوى نظام تضخيم",
        "زيادة الكتلة العضلية",
        "أفضل تمارين التضخيم",
        "خطة بناء العضلات",
        "أفضل مكملات التضخيم",
        "كيف تبني عضلات بسرعة",
    ],
    "تغذية": [
        "أفضل نظام غذائي رياضي",
        "أهمية البروتين للعضلات",
        "التغذية الصحية للرياضيين",
        "كيف تحسب سعراتك الحرارية",
        "أفضل وجبات بعد التمرين",
    ],
    "تمارين": [
        "أفضل تمارين الصدر",
        "أقوى تمارين الظهر",
        "تمارين الأرجل الصحيحة",
        "كيفية تمرين الكتف",
        "أفضل جدول تدريبي أسبوعي",
    ]
}

# =========================================================
# USED POSTS SYSTEM
# =========================================================

def load_used_posts():
    if not USED_POSTS_FILE.exists():
        return []

    try:
        with open(USED_POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return []


def save_used_post(title):

    posts = load_used_posts()

    posts.append(title)

    with open(USED_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)


# =========================================================
# UTILITIES
# =========================================================

def trigger_vercel_deploy():

    if not VERCEL_HOOK:
        print("⚠️ No Vercel Hook Found")
        return

    try:

        response = requests.post(
            VERCEL_HOOK,
            timeout=10
        )

        if response.status_code in [200, 201]:
            print("🚀 Vercel Deployment Started!")

    except Exception as e:
        print(f"⚠️ Deploy Error: {e}")


def clean_text(text):

    text = text.strip()

    text = text.replace("##", "")
    text = text.replace("###", "")
    text = text.replace("*", "")

    return text


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
# FORMAT ARTICLE
# =========================================================

def format_content(text):

    text = clean_text(text)

    paragraphs = text.split("\n")

    formatted = ""

    for p in paragraphs:

        p = p.strip()

        if not p:
            continue

        # عناوين
        if (
            len(p) < 90
            and (
                ":" in p
                or "فوائد" in p
                or "أهمية" in p
                or "تمارين" in p
                or "نصائح" in p
                or "خاتمة" in p
            )
        ):

            formatted += f"""
            <h2 class="
            text-4xl
            font-black
            text-slate-900
            mt-16
            mb-8
            border-r-[12px]
            border-blue-600
            pr-6
            py-5
            bg-white
            rounded-[2rem]
            shadow-lg
            text-right
            ">
            {p}
            </h2>
            """

        else:

            style = random.choice(paragraph_styles)

            formatted += f"""
            <div class="
            {style}
            p-10
            rounded-[2.5rem]
            shadow-md
            leading-[2.8rem]
            text-[22px]
            mb-10
            font-medium
            text-right
            transition-all
            hover:scale-[1.01]
            ">
            {p}
            </div>
            """

    return formatted


# =========================================================
# SITEMAP
# =========================================================

def update_sitemap(slug):

    today = datetime.date.today().strftime("%Y-%m-%d")

    url = f"{DOMAIN}/{slug}"

    if not SITEMAP_FILE.exists():

        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

<url>
<loc>{DOMAIN}</loc>
<lastmod>{today}</lastmod>
</url>

</urlset>
"""

        SITEMAP_FILE.write_text(
            sitemap,
            encoding="utf-8"
        )

    content = SITEMAP_FILE.read_text(
        encoding="utf-8"
    )

    if url in content:
        return

    new_url = f"""

<url>
<loc>{url}</loc>
<lastmod>{today}</lastmod>
</url>

</urlset>
"""

    updated = content.replace(
        "</urlset>",
        new_url
    )

    SITEMAP_FILE.write_text(
        updated,
        encoding="utf-8"
    )

    print("✅ Sitemap Updated")


# =========================================================
# BLOG PAGE
# =========================================================

def create_blog_page_if_not_exists():

    if BLOG_FILE.exists():
        return

    html = """
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TDEE Arabia Blog</title>

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

body{
    font-family:'Cairo',sans-serif;
}

</style>

</head>

<body class="bg-slate-100">

<!-- HEADER -->

<header class="bg-white shadow-md sticky top-0 z-50">

<div class="max-w-7xl mx-auto px-6 py-6">

<div class="flex flex-col md:flex-row gap-6 justify-between items-center">

<h1 class="text-4xl font-black text-blue-600">
TDEE ARABIA 🔥
</h1>

<input
id="searchInput"
type="text"
placeholder="ابحث عن مقال..."
class="
w-full
md:w-[350px]
px-6
py-4
rounded-2xl
border-2
border-slate-200
focus:outline-none
focus:border-blue-500
text-right
font-bold
"
/>

</div>

<!-- FILTERS -->

<div class="flex flex-wrap gap-4 mt-6 justify-center">

<button onclick="filterPosts('all')" class="filter-btn bg-slate-900 text-white px-6 py-3 rounded-2xl font-black">
الكل
</button>

<button onclick="filterPosts('تنشيف')" class="filter-btn bg-blue-500 text-white px-6 py-3 rounded-2xl font-black">
تنشيف
</button>

<button onclick="filterPosts('تضخيم')" class="filter-btn bg-emerald-500 text-white px-6 py-3 rounded-2xl font-black">
تضخيم
</button>

<button onclick="filterPosts('تغذية')" class="filter-btn bg-orange-500 text-white px-6 py-3 rounded-2xl font-black">
تغذية
</button>

<button onclick="filterPosts('تمارين')" class="filter-btn bg-purple-500 text-white px-6 py-3 rounded-2xl font-black">
تمارين
</button>

</div>

</div>

</header>

<!-- POSTS -->

<main class="max-w-7xl mx-auto px-6 py-16">

<div
id="blog-grid"
class="
grid
grid-cols-1
md:grid-cols-2
xl:grid-cols-3
gap-12
"
>

PLACEHOLDER_MARKER

</div>

</main>

<script>

const searchInput = document.getElementById("searchInput")

searchInput.addEventListener("keyup", function(){

    const value = this.value.toLowerCase()

    const posts = document.querySelectorAll(".blog-card")

    posts.forEach(post=>{

        const title = post
        .querySelector(".post-title")
        .innerText
        .toLowerCase()

        if(title.includes(value)){
            post.style.display = "block"
        }else{
            post.style.display = "none"
        }

    })

})

function filterPosts(category){

    const posts = document.querySelectorAll(".blog-card")

    posts.forEach(post=>{

        if(
            category === "all"
            ||
            post.dataset.category === category
        ){
            post.style.display = "block"
        }else{
            post.style.display = "none"
        }

    })

}

</script>

</body>

</html>
"""

    BLOG_FILE.write_text(
        html,
        encoding="utf-8"
    )

    print("✅ Blog Page Created")


# =========================================================
# ADD BLOG CARD
# =========================================================

def add_blog_card(
    slug,
    title,
    image,
    category
):

    create_blog_page_if_not_exists()

    today = datetime.date.today().strftime(
        "%Y-%m-%d"
    )

    card = f"""

<div
class="
blog-card
bg-white
rounded-[3rem]
overflow-hidden
shadow-xl
hover:shadow-2xl
transition-all
duration-300
"
data-category="{category}"
>

<img
src="{image}"
class="w-full h-72 object-cover"
alt="{title}"
>

<div class="p-10 text-right">

<span class="
inline-block
bg-blue-100
text-blue-700
px-4
py-2
rounded-xl
font-black
mb-5
">
{category}
</span>

<h2 class="
post-title
text-3xl
font-black
text-slate-900
leading-[3rem]
mb-6
">
{title}
</h2>

<p class="
text-slate-500
font-bold
mb-8
">
📅 {today}
</p>

<a
href="./{slug}"
class="
block
w-full
text-center
bg-slate-900
hover:bg-blue-600
transition-all
text-white
font-black
py-5
rounded-2xl
text-xl
"
>

إقرأ المقال ←

</a>

</div>

</div>

"""

    content = BLOG_FILE.read_text(
        encoding="utf-8"
    )

    updated = content.replace(
        "PLACEHOLDER_MARKER",
        f"{card}\nPLACEHOLDER_MARKER"
    )

    BLOG_FILE.write_text(
        updated,
        encoding="utf-8"
    )

    print("✅ Blog Card Added")


# =========================================================
# GENERATE ARTICLE
# =========================================================

def generate_article(title, category):

    prompt = f"""

اكتب مقال عربي احترافي جدا عن:

{title}

التصنيف:
{category}

شروط المقال:

- 2000 كلمة
- أسلوب بشري احترافي
- SEO قوي
- بدون تكرار
- معلومات رياضية دقيقة
- مقدمة قوية
- خاتمة قوية
- فقرات طويلة
- عناوين واضحة
- بدون markdown
- بدون رموز نجوم
- لغة عربية ممتازة

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
        max_tokens=5000
    )

    return response.choices[0].message.content


# =========================================================
# CREATE POST PAGE
# =========================================================

def create_post_page(
    title,
    category,
    body,
    image,
    slug
):

    today = datetime.date.today().strftime(
        "%Y-%m-%d"
    )

    html = f"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>

<meta
name="description"
content="{title} - أفضل مقالات الرياضة والتغذية"
>

<link
rel="canonical"
href="{DOMAIN}/{slug}"
>

<meta property="og:title" content="{title}">
<meta property="og:image" content="{image}">
<meta property="og:type" content="article">

<script src="https://cdn.tailwindcss.com"></script>

<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">

<style>

body{
    font-family:'Cairo',sans-serif;
    background:#f1f5f9;
}

</style>

</head>

<body>

<!-- HEADER -->

<header class="
bg-white
shadow-md
sticky
top-0
z-50
">

<div class="
max-w-6xl
mx-auto
px-6
py-6
flex
justify-between
items-center
">

<a href="./blog.html" class="
text-blue-600
font-black
text-4xl
">
TDEE ARABIA 🔥
</a>

</div>

</header>

<!-- ARTICLE -->

<main class="
max-w-5xl
mx-auto
px-6
py-16
">

<img
src="{image}"
class="
w-full
rounded-[3rem]
shadow-2xl
mb-12
max-h-[550px]
object-cover
"
alt="{title}"
>

<span class="
inline-block
bg-blue-600
text-white
font-black
px-5
py-3
rounded-2xl
mb-8
text-xl
">
{category}
</span>

<h1 class="
text-5xl
font-black
text-slate-900
leading-[5rem]
mb-8
text-right
">
{title}
</h1>

<div class="
text-right
text-slate-500
font-bold
mb-14
text-xl
">
📅 {today}
</div>

{body}

</main>

</body>

</html>
"""

    post_path = BASE_DIR / slug

    post_path.write_text(
        html,
        encoding="utf-8"
    )

    print(f"✅ Post Created: {slug}")


# =========================================================
# GENERATE UNIQUE TITLE
# =========================================================

def generate_unique_post():

    used_posts = load_used_posts()

    available = []

    for category, items in topics.items():

        for title in items:

            full_title = title + " 2026"

            if full_title not in used_posts:

                available.append(
                    (
                        category,
                        full_title
                    )
                )

    if not available:

        raise Exception(
            "❌ جميع المواضيع استعملت"
        )

    return random.choice(available)


# =========================================================
# MAIN
# =========================================================

def generate_post():

    try:

        category, title = generate_unique_post()

        print(f"🚀 Generating: {title}")

        article = generate_article(
            title,
            category
        )

        formatted = format_content(
            article
        )

        slug = generate_slug(title)

        image = f"https://loremflickr.com/1200/800/gym?lock={random.randint(1,999999)}"

        create_post_page(
            title,
            category,
            formatted,
            image,
            slug
        )

        add_blog_card(
            slug,
            title,
            image,
            category
        )

        update_sitemap(slug)

        save_used_post(title)

        trigger_vercel_deploy()

        print("🎉 DONE SUCCESSFULLY")

    except Exception as e:

        print(f"❌ ERROR: {e}")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    generate_post()
