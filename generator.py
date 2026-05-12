import os
import random
import datetime
import re
import hashlib
from groq import Groq

# ═══════════════════════════════════════════════
#  إعداد العميل
# ═══════════════════════════════════════════════
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
DOMAIN = "https://tdee-arabia.vercel.app"

# ═══════════════════════════════════════════════
#  الصور — Picsum بـ seed ثابت لكل مقال (بدل source.unsplash المتوقف)
#  أو Unsplash عبر source.unsplash مع fallback
# ═══════════════════════════════════════════════
UNSPLASH_COLLECTIONS = {
    "تنشيف":  ["1571019614242-c5c5dee81b7a", "1534438327276-14e5300c3a48", "1517836357463-d25dfeac3438"],
    "تضخيم":  ["1581009146145-b5ef050c2e1e", "1583454110551-21f2fa2afe61", "1526506118085-60ce8714f8c5"],
    "مكملات": ["1593095948071-474c5cc2989d", "1550345332-09519ac5dca8", "1540497077202-9b5ce89f8a63"],
}

def get_image_url(category: str, seed: int) -> str:
    """صورة ثابتة لكل مقال بناءً على الـ seed — تضمن عدم التكرار"""
    ids = UNSPLASH_COLLECTIONS.get(category, UNSPLASH_COLLECTIONS["تنشيف"])
    photo_id = ids[seed % len(ids)]
    # نضيف الـ seed في المعاملات حتى يختلف crop كل مرة
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=1200&q=80&h=700&crop=entropy&seed={seed}"

# ═══════════════════════════════════════════════
#  تنسيق المحتوى — تصميم مجلة احترافية
# ═══════════════════════════════════════════════
SECTION_ICONS = ["💪", "🔥", "⚡", "🎯", "✅", "🏆", "💡", "📌"]

def format_content(text: str) -> str:
    # تنظيف: نحذف كل ما ليس عربياً أو أرقاماً أو علامات ترقيم أساسية
    text = re.sub(r'[^\u0600-\u06FF\s\d\.\:\-\!\?\(\)\*،؛«»]', '', text)
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    html_parts = []
    icon_index = 0

    for p in paragraphs:
        if p.startswith('**') and p.endswith('**'):
            # ─── عنوان قسم ───
            title = p.replace('**', '').strip()
            icon = SECTION_ICONS[icon_index % len(SECTION_ICONS)]
            icon_index += 1
            html_parts.append(f'''
<div class="section-heading">
  <span class="section-icon">{icon}</span>
  <h2>{title}</h2>
</div>''')

        elif p.startswith('* '):
            # ─── نقطة قائمة ───
            item = p[2:].strip()
            html_parts.append(f'''
<div class="list-item">
  <span class="bullet">◆</span>
  <span>{item}</span>
</div>''')

        else:
            # ─── فقرة عادية ───
            html_parts.append(f'<p class="body-para">{p}</p>')

    return '\n'.join(html_parts)


# ═══════════════════════════════════════════════
#  Sitemap
# ═══════════════════════════════════════════════
def update_sitemap(file_slug: str):
    sitemap_file = "sitemap.xml"
    url = f"{DOMAIN}/{file_slug}"
    today = datetime.date.today().isoformat()

    if not os.path.exists(sitemap_file):
        content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>
  <url><loc>{DOMAIN}/blog.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>
</urlset>'''
        with open(sitemap_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(sitemap_file, "r", encoding="utf-8") as f:
            content = f.read()
        if url not in content:
            new_entry = f'  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>\n'
            content = content.replace("</urlset>", new_entry + "</urlset>")
            with open(sitemap_file, "w", encoding="utf-8") as f:
                f.write(content)


# ═══════════════════════════════════════════════
#  بطاقة المقال في صفحة المدونة
# ═══════════════════════════════════════════════
BLOG_CARD_MARKER = "<!-- CARDS_START -->"

def update_blog_list(file_slug: str, title: str, image_url: str, category: str):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%d/%m/%Y")

    cat_colors = {
        "تنشيف":  ("var(--accent-orange)", "🔥"),
        "تضخيم":  ("var(--accent-green)",  "💪"),
        "مكملات": ("var(--accent-blue)",   "⚡"),
    }
    cat_color, cat_emoji = cat_colors.get(category, ("var(--accent-blue)", "📌"))

    new_card = f'''
    <article class="card" data-category="{category}">
      <a href="/{file_slug}" class="card-img-wrap">
        <img src="{image_url}"
             alt="{title}"
             loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=800'">
        <span class="card-badge" style="background:{cat_color}">{cat_emoji} {category}</span>
      </a>
      <div class="card-body">
        <time class="card-date">{today}</time>
        <h3 class="card-title">{title}</h3>
        <a href="/{file_slug}" class="card-btn">قراءة المقال <span>←</span></a>
      </div>
    </article>'''

    if not os.path.exists(blog_file):
        _create_blog_html(blog_file, new_card)
    else:
        with open(blog_file, "r", encoding="utf-8") as f:
            content = f.read()

        if BLOG_CARD_MARKER in content:
            # أضف البطاقة الجديدة مباشرة بعد الـ marker (أحدث المقالات أولاً)
            content = content.replace(
                BLOG_CARD_MARKER,
                BLOG_CARD_MARKER + new_card
            )
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print("⚠️  تحذير: BLOG_CARD_MARKER غير موجود في blog.html")


def _create_blog_html(path: str, first_card: str):
    """ينشئ blog.html من الصفر إذا لم يوجد"""
    html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="مجلة TDEE Arabia الرياضية — مقالات في التغذية، التنشيف، التضخيم والمكملات">
<title>المدونة الرياضية | TDEE Arabia</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&family=Cairo+Play:wght@700;900&display=swap" rel="stylesheet">
<style>
/* ═══════ CSS Variables ═══════ */
:root {{
  --bg:            #0d0f14;
  --surface:       #161921;
  --surface2:      #1e2230;
  --border:        rgba(255,255,255,.06);
  --text:          #e8eaf0;
  --text-muted:    #7a8099;
  --accent-orange: #ff6b35;
  --accent-green:  #22c55e;
  --accent-blue:   #3b82f6;
  --accent-gold:   #f59e0b;
  --radius-card:   1.5rem;
  --font-display:  'Cairo Play', sans-serif;
  --font-body:     'Tajawal', sans-serif;
  --transition:    .3s cubic-bezier(.4,0,.2,1);
}}

/* ═══════ Reset ═══════ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  direction: rtl;
  text-align: right;
}}
img {{ display: block; max-width: 100%; }}
a {{ color: inherit; text-decoration: none; }}

/* ═══════ Navbar ═══════ */
.navbar {{
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(13,15,20,.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}}
.navbar .logo {{
  font-family: var(--font-display);
  font-size: 1.4rem; font-weight: 900;
  color: #fff;
  display: flex; align-items: center; gap: .4rem;
}}
.logo em {{ color: var(--accent-orange); font-style: normal; }}
.navbar a.home-link {{
  font-size: .9rem; font-weight: 700;
  color: var(--text-muted);
  transition: color var(--transition);
}}
.navbar a.home-link:hover {{ color: var(--accent-orange); }}

/* ═══════ Hero ═══════ */
.hero {{
  text-align: center;
  padding: 5rem 1rem 3rem;
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, rgba(255,107,53,.12), transparent),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(59,130,246,.08), transparent);
}}
.hero-tag {{
  display: inline-block;
  font-size: .75rem; font-weight: 700; letter-spacing: .15em;
  text-transform: uppercase;
  color: var(--accent-orange);
  border: 1px solid rgba(255,107,53,.3);
  border-radius: 99px;
  padding: .3rem 1rem;
  margin-bottom: 1.5rem;
}}
.hero h1 {{
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 6vw, 4.5rem);
  font-weight: 900;
  line-height: 1.1;
  color: #fff;
  margin-bottom: 1rem;
}}
.hero h1 em {{ color: var(--accent-orange); font-style: normal; }}
.hero p {{
  font-size: 1.1rem; color: var(--text-muted);
  max-width: 480px; margin: 0 auto 2.5rem;
  line-height: 1.8;
}}

/* ═══════ Search + Filters ═══════ */
.controls {{
  max-width: 700px; margin: 0 auto;
  display: flex; flex-direction: column; gap: 1rem;
}}
.search-wrap {{
  position: relative;
}}
.search-wrap input {{
  width: 100%;
  padding: .85rem 1.2rem .85rem 3rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 99px;
  color: var(--text);
  font-family: var(--font-body); font-size: 1rem;
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
}}
.search-wrap input::placeholder {{ color: var(--text-muted); }}
.search-wrap input:focus {{
  border-color: rgba(255,107,53,.4);
  box-shadow: 0 0 0 3px rgba(255,107,53,.08);
}}
.search-wrap .search-icon {{
  position: absolute; left: 1rem; top: 50%; transform: translateY(-50%);
  color: var(--text-muted); font-size: 1.1rem; pointer-events: none;
}}
.filters {{
  display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center;
}}
.filter-btn {{
  padding: .45rem 1.1rem;
  border-radius: 99px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-family: var(--font-body); font-size: .85rem; font-weight: 700;
  cursor: pointer; transition: all var(--transition);
}}
.filter-btn:hover, .filter-btn.active {{
  background: var(--accent-orange);
  border-color: var(--accent-orange);
  color: #fff;
}}

/* ═══════ Grid ═══════ */
.section-label {{
  max-width: 1200px; margin: 4rem auto 1.5rem;
  padding: 0 1.5rem;
  font-size: .8rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--text-muted);
  border-right: 3px solid var(--accent-orange);
  padding-right: .75rem;
}}
.grid {{
  max-width: 1200px; margin: 0 auto 5rem;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.75rem;
}}

/* ═══════ Card ═══════ */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  overflow: hidden;
  display: flex; flex-direction: column;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
}}
.card:hover {{
  transform: translateY(-6px);
  box-shadow: 0 20px 60px rgba(0,0,0,.4);
  border-color: rgba(255,107,53,.25);
}}
.card-img-wrap {{
  position: relative;
  height: 220px; overflow: hidden; flex-shrink: 0;
}}
.card-img-wrap img {{
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .6s ease;
}}
.card:hover .card-img-wrap img {{ transform: scale(1.06); }}
.card-badge {{
  position: absolute; top: .9rem; right: .9rem;
  padding: .3rem .85rem;
  border-radius: 99px;
  font-size: .72rem; font-weight: 700;
  color: #fff;
  backdrop-filter: blur(8px);
}}
.card-body {{
  padding: 1.4rem;
  display: flex; flex-direction: column; gap: .75rem;
  flex: 1;
}}
.card-date {{
  font-size: .75rem; color: var(--text-muted); font-weight: 500;
}}
.card-title {{
  font-family: var(--font-display);
  font-size: 1.1rem; font-weight: 900; line-height: 1.45;
  color: #fff;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.card-btn {{
  margin-top: auto;
  display: inline-flex; align-items: center; gap: .4rem;
  padding: .65rem 1.1rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: .75rem;
  font-size: .85rem; font-weight: 700;
  color: var(--text);
  transition: all var(--transition);
  width: fit-content;
}}
.card-btn:hover {{
  background: var(--accent-orange);
  border-color: var(--accent-orange);
  color: #fff;
}}

/* ═══════ Empty State ═══════ */
.empty-state {{
  grid-column: 1/-1;
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-muted);
}}
.empty-state span {{ font-size: 3rem; display: block; margin-bottom: 1rem; }}

/* ═══════ Footer ═══════ */
footer {{
  border-top: 1px solid var(--border);
  text-align: center;
  padding: 2rem 1rem;
  font-size: .85rem; color: var(--text-muted);
}}

/* ═══════ Responsive ═══════ */
@media (max-width: 600px) {{
  .grid {{ grid-template-columns: 1fr; }}
  .hero h1 {{ font-size: 2rem; }}
  .navbar {{ padding: .85rem 1rem; }}
}}

/* ═══════ Hidden ═══════ */
.card.hidden {{ display: none; }}
</style>
</head>
<body>

<!-- NAV -->
<nav class="navbar">
  <div class="logo">TDEE <em>ARABIA</em> 🔥</div>
  <a href="/" class="home-link">← الرئيسية</a>
</nav>

<!-- HERO -->
<header class="hero">
  <span class="hero-tag">✦ المجلة الرياضية</span>
  <h1>محتوى رياضي<br><em>باحترافية حقيقية</em></h1>
  <p>تنشيف · تضخيم · تغذية · مكملات — كل ما تحتاجه في مكان واحد</p>

  <div class="controls">
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input type="text" id="searchInput" placeholder="ابحث عن موضوع...">
    </div>
    <div class="filters">
      <button class="filter-btn active" onclick="filterPosts('الكل', this)">الكل</button>
      <button class="filter-btn" onclick="filterPosts('تنشيف', this)">🔥 تنشيف</button>
      <button class="filter-btn" onclick="filterPosts('تضخيم', this)">💪 تضخيم</button>
      <button class="filter-btn" onclick="filterPosts('مكملات', this)">⚡ مكملات</button>
    </div>
  </div>
</header>

<!-- GRID -->
<p class="section-label">آخر المقالات</p>
<main class="grid" id="blog-grid">
  {BLOG_CARD_MARKER}
  {first_card}
</main>

<footer>
  <p>© {datetime.date.today().year} TDEE Arabia — جميع الحقوق محفوظة</p>
</footer>

<script>
const input = document.getElementById('searchInput');
const cards = () => document.querySelectorAll('.card');

input.addEventListener('input', () => {{
  const q = input.value.trim().toLowerCase();
  cards().forEach(c => {{
    const title = c.querySelector('.card-title')?.textContent.toLowerCase() ?? '';
    c.classList.toggle('hidden', q && !title.includes(q));
  }});
  checkEmpty();
}});

function filterPosts(cat, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  input.value = '';
  cards().forEach(c => {{
    c.classList.toggle('hidden', cat !== 'الكل' && c.dataset.category !== cat);
  }});
  checkEmpty();
}}

function checkEmpty() {{
  const grid = document.getElementById('blog-grid');
  const visible = [...cards()].filter(c => !c.classList.contains('hidden'));
  let empty = grid.querySelector('.empty-state');
  if (visible.length === 0) {{
    if (!empty) {{
      empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = '<span>🔍</span><p>لا توجد نتائج مطابقة</p>';
      grid.appendChild(empty);
    }}
  }} else if (empty) {{
    empty.remove();
  }}
}}
</script>
</body>
</html>'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ═══════════════════════════════════════════════
#  HTML المقال الفردي — تصميم مجلة
# ═══════════════════════════════════════════════
def build_article_html(title: str, category: str, image_url: str, body_html: str, file_slug: str) -> str:
    today = datetime.date.today().strftime("%d %B %Y")
    cat_emoji = {"تنشيف": "🔥", "تضخيم": "💪", "مكملات": "⚡"}.get(category, "📌")

    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{title} — مقال رياضي من TDEE Arabia">
<title>{title} | TDEE Arabia</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&family=Cairo+Play:wght@700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:          #0d0f14;
  --surface:     #161921;
  --surface2:    #1e2230;
  --border:      rgba(255,255,255,.06);
  --text:        #d8dae6;
  --text-muted:  #7a8099;
  --accent:      #ff6b35;
  --radius:      1.25rem;
  --font-display:'Cairo Play', sans-serif;
  --font-body:   'Tajawal', sans-serif;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  direction: rtl; text-align: right;
  line-height: 1.9;
}}
img {{ display: block; max-width: 100%; }}
a {{ color: var(--accent); text-decoration: none; }}

/* NAV */
.navbar {{
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(13,15,20,.9);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}}
.logo {{ font-family: var(--font-display); font-size: 1.3rem; font-weight: 900; color: #fff; }}
.logo em {{ color: var(--accent); font-style: normal; }}
.back-link {{ font-size: .85rem; font-weight: 700; color: var(--text-muted); transition: color .2s; }}
.back-link:hover {{ color: var(--accent); }}

/* HERO IMG */
.hero-img {{
  width: 100%; height: clamp(280px, 45vw, 520px);
  object-fit: cover;
  object-position: center;
  display: block;
}}
.hero-overlay {{
  position: relative;
  background: linear-gradient(to top, rgba(13,15,20,1) 10%, rgba(13,15,20,.3) 60%, transparent);
  margin-top: -4px;
  padding: 3rem 0 0;
}}

/* ARTICLE WRAPPER */
.article-wrap {{
  max-width: 800px; margin: 0 auto;
  padding: 0 1.5rem 5rem;
}}
.article-meta {{
  display: flex; align-items: center; gap: .75rem; flex-wrap: wrap;
  margin-bottom: 1.25rem;
}}
.badge {{
  padding: .3rem .9rem;
  border-radius: 99px;
  background: var(--accent);
  color: #fff; font-size: .75rem; font-weight: 700;
}}
.meta-date {{ font-size: .8rem; color: var(--text-muted); }}
.article-title {{
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 900; line-height: 1.2;
  color: #fff; margin-bottom: 2.5rem;
}}

/* DIVIDER */
.divider {{
  width: 60px; height: 3px;
  background: var(--accent);
  border-radius: 99px;
  margin: 0 0 2.5rem;
}}

/* CONTENT */
.article-body {{ display: flex; flex-direction: column; gap: 1.25rem; }}

.section-heading {{
  display: flex; align-items: center; gap: .75rem;
  padding: 1rem 1.25rem;
  background: var(--surface);
  border-right: 4px solid var(--accent);
  border-radius: 0 var(--radius) var(--radius) 0;
  margin-top: 1rem;
}}
.section-icon {{ font-size: 1.3rem; }}
.section-heading h2 {{
  font-family: var(--font-display);
  font-size: 1.25rem; font-weight: 900; color: #fff;
}}

.body-para {{
  font-size: 1.05rem; color: var(--text);
  padding: 1.25rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}}

.list-item {{
  display: flex; align-items: baseline; gap: .75rem;
  padding: .85rem 1.25rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: .85rem;
  font-size: 1rem; font-weight: 500;
}}
.bullet {{ color: var(--accent); font-size: .6rem; flex-shrink: 0; margin-top: .2rem; }}

/* BACK BTN */
.back-btn {{
  display: inline-flex; align-items: center; gap: .5rem;
  margin-top: 3rem;
  padding: .75rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 99px;
  font-size: .9rem; font-weight: 700; color: var(--text);
  transition: all .2s;
}}
.back-btn:hover {{
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}}

@media (max-width: 600px) {{
  .navbar {{ padding: .85rem 1rem; }}
  .article-body {{ gap: 1rem; }}
}}
</style>
</head>
<body>

<nav class="navbar">
  <div class="logo">TDEE <em>ARABIA</em> 🔥</div>
  <a href="/blog.html" class="back-link">← المدونة</a>
</nav>

<img src="{image_url}"
     alt="{title}"
     class="hero-img"
     onerror="this.src='https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200'">

<div class="hero-overlay">
  <div class="article-wrap">
    <div class="article-meta">
      <span class="badge">{cat_emoji} {category}</span>
      <span class="meta-date">{today}</span>
    </div>
    <h1 class="article-title">{title}</h1>
    <div class="divider"></div>

    <div class="article-body">
      {body_html}
    </div>

    <a href="/blog.html" class="back-btn">← العودة للمدونة</a>
  </div>
</div>

</body>
</html>'''


# ═══════════════════════════════════════════════
#  الدالة الرئيسية
# ═══════════════════════════════════════════════
TOPICS = {
    "تنشيف": [
        "تنشيف الجسم", "حرق الدهون", "دايت الكيتو", "برنامج تنشيف",
        "أفضل تمارين الكارديو", "تقليل الكربوهيدرات",
    ],
    "تضخيم": [
        "بناء العضلات", "برنامج التضخيم", "تضخيم الكتفين",
        "أفضل تمارين الصدر", "تضخيم الأرجل", "زيادة الكتلة العضلية",
    ],
    "مكملات": [
        "أفضل مكملات غذائية", "دليل الكرياتين", "أنواع البروتين",
        "مكملات ما قبل التمرين", "فيتامينات الرياضيين", "الكولاجين للرياضيين",
    ],
}

def generate():
    category = random.choice(list(TOPICS.keys()))
    topic    = random.choice(TOPICS[category])
    weight   = random.randint(60, 115)
    title    = f"{topic} لوزن {weight} كجم"

    # seed ثابت مشتق من العنوان — يضمن عدم تكرار نفس الصورة لنفس المقال
    seed = int(hashlib.md5(title.encode()).hexdigest(), 16) % 10000
    image_url = get_image_url(category, seed)

    print(f"⚙️  جاري توليد: {title}")

    try:
        res = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": (
                    f"اكتب مقال SEO احترافي بالعربية الفصحى فقط عن: {title}\n"
                    "الشروط:\n"
                    "- استخدم عناوين فرعية بين ** مثل: **عنوان القسم**\n"
                    "- استخدم نقاط القوائم بـ * مثل: * عنصر القائمة\n"
                    "- الفقرات العادية بدون أي رمز في البداية\n"
                    "- اكتب بالعربية الفصحى فقط، بدون أي رموز إنجليزية أو خاصة\n"
                    "- المقال لا يقل عن 600 كلمة"
                )
            }],
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            temperature=0.7,
        )
        raw_text = res.choices[0].message.content
        body_html = format_content(raw_text)

        # اسم الملف: slug مشتق من hash لضمان الفرادة وتجنب الكتابة فوق ملف موجود
        file_slug = f"post-{seed}-{random.randint(100,999)}.html"
        article_html = build_article_html(title, category, image_url, body_html, file_slug)

        with open(file_slug, "w", encoding="utf-8") as f:
            f.write(article_html)

        update_blog_list(file_slug, title, image_url, category)
        update_sitemap(file_slug)

        print(f"✅ نُشر بنجاح: {title}")
        print(f"   📄 الملف : {file_slug}")
        print(f"   🖼️  الصورة: {image_url}")

    except Exception as e:
        print(f"❌ خطأ أثناء التوليد: {e}")
        raise


if __name__ == "__main__":
    generate()
