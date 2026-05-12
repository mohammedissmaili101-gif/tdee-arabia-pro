import os
import random
import datetime
from groq import Groq

# إعداد العميل
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# روابط صور رياضية مباشرة عالية الاستقرار (Pexels & Unsplash Direct)
gym_images = [
    "https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/414029/pexels-photo-414029.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/949126/pexels-photo-949126.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2261146/pexels-photo-2261146.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2827392/pexels-photo-2827392.jpeg?auto=compress&cs=tinysrgb&w=800"
]

def update_blog_list(file_slug, title, image_url):
    blog_file = "blog.html"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # تصميم البطاقة باحترافية عالية
    new_card = f"""
    <div class="bg-white rounded-3xl shadow-xl overflow-hidden hover:scale-[1.02] transition-all duration-300 border border-slate-100 flex flex-col">
        <div class="relative">
            <img src="{image_url}" alt="{title}" class="w-full h-52 object-cover" onerror="this.src='https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800'">
            <div class="absolute top-4 right-4 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">جديد</div>
        </div>
        <div class="p-6 flex-grow flex flex-col">
            <div class="flex items-center gap-2 mb-3 text-slate-400 text-sm font-medium">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                {today}
            </div>
            <h3 class="text-xl font-black mb-6 text-slate-900 leading-tight h-14 overflow-hidden">{title}</h3>
            <a href="/{file_slug}" class="mt-auto inline-block w-full text-center bg-blue-600 text-white font-bold py-3.5 rounded-2xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200">إقرأ التفاصيل</a>
        </div>
    </div>
    """

    if not os.path.exists(blog_file):
        # هيكل الصفحة الأساسي مع Tailwind CSS وتحسين SEO
        initial_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>المدونة الصحية | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo',sans-serif;}}</style></head><body class="bg-slate-50 text-right"><nav class="bg-white shadow-sm sticky top-0 z-50 p-5 mb-10"><div class="max-w-6xl mx-auto flex justify-between items-center"><h1 class="text-2xl font-black text-blue-600 tracking-tighter italic">TDEE ARABIA 🔥</h1><div class="flex gap-6 font-bold text-slate-600"><a href="/" class="hover:text-blue-600">الرئيسية</a><a href="/blog.html" class="text-blue-600 border-b-2 border-blue-600">المدونة</a></div></div></nav><main class="max-w-6xl mx-auto px-4"><div class="text-center mb-16"><h2 class="text-4xl md:text-5xl font-black mb-4 text-slate-900">أحدث أسرار اللياقة البدنية</h2><p class="text-slate-500 text-lg">نقدم لك يومياً نصائح علمية مدعومة بالذكاء الاصطناعي لتحقيق جسم أحلامك</p></div><div id="blog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-20">{new_card}</div></main></body></html>"""
        with open(blog_file, "w", encoding="utf-8") as f: f.write(initial_html)
    else:
        with open(blog_file, "r", encoding="utf-8") as f: content = f.read()
        marker = 'id="blog-grid">'
        # إضافة المقال الجديد في المقدمة دائماً
        new_content = content.replace(marker, marker + "\n" + new_card)
        with open(blog_file, "w", encoding="utf-8") as f: f.write(new_content)

def generate():
    # توسيع ضخم للمواضيع لضمان عدم التكرار
    main_topics = [
        "أسرار تضخيم العضلات الطبيعي", "خطة التنشيف النهائية لخسارة الدهون", 
        "أفضل مصادر البروتين الاقتصادي", "دليل المكملات الغذائية للمبتدئين",
        "تمارين الكارديو لحرق السعرات بفعالية", "كيفية حساب سعرات التثبيت",
        "تأثير النوم على نمو العضلات", "وجبات ما قبل التمرين للطاقة القصوى",
        "تجنب إصابات الظهر أثناء التمارين", "طرق تسريع الاستشفاء العضلي"
    ]
    
    selected_topic = random.choice(main_topics)
    weight = random.randint(55, 110)
    image = random.choice(gym_images)
    title = f"{selected_topic} - دليل شامل لمن وزنه {weight} كجم"
    
    try:
        # طلب مقال SEO احترافي جداً
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"اكتب مقال SEO احترافي جداً بالعربية عن {title}. ابدأ بمقدمة جذابة، استخدم عناوين فرعية (H2, H3)، فقرات قصيرة، وجدول نصائح في النهاية. اجعل المقال مفصلاً وعلمياً."}],
            model="llama-3.3-70b-versatile",
        )
        body = res.choices[0].message.content.replace('\n', '<br>')
        file_slug = f"post-{random.randint(10000, 99999)}.html"

        # قالب المقال الفردي (Article Page)
        article_html = f"""
        <!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title} | TDEE Arabia</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{{font-family:'Cairo',sans-serif;}}</style></head>
        <body class="bg-slate-50 text-right"><nav class="bg-white/80 backdrop-blur-md sticky top-0 z-50 p-4 border-b"><div class="max-w-4xl mx-auto flex justify-between items-center"><a href="/blog.html" class="text-blue-600 font-bold flex items-center gap-2"><span>←</span> العودة للمدونة</a><span class="font-black text-slate-800">TDEE ARABIA</span></div></nav>
        <main class="max-w-4xl mx-auto my-12 px-4"><div class="relative mb-12"><img src="{image}" class="w-full h-[450px] object-cover rounded-[3rem] shadow-2xl transition-transform hover:scale-[1.01] duration-500" onerror="this.src='https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800'"><div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-[3rem]"></div><div class="absolute bottom-10 right-10 left-10 text-white"><h1 class="text-3xl md:text-5xl font-black leading-tight mb-2">{title}</h1><div class="bg-blue-600 w-20 h-1.5 rounded-full"></div></div></div>
        <article class="bg-white p-8 md:p-16 rounded-[3rem] shadow-xl border border-slate-100 mb-20"><div class="prose prose-lg max-w-none text-slate-700 leading-relaxed space-y-8 text-xl">{body}</div></article></main>
        <footer class="bg-slate-900 text-white py-12 text-center mt-20"><p class="font-bold opacity-60">جميع الحقوق محفوظة © TDEE ARABIA 2026</p></footer>
        </body></html>
        """
        
        with open(file_slug, "w", encoding="utf-8") as f: f.write(article_html)
        update_blog_list(file_slug, title, image)
        print(f"✅ تم إنشاء المقال بنجاح: {file_slug}")
    except Exception as e:
        print(f"❌ خطأ في النظام: {e}")

if __name__ == "__main__":
    generate()
