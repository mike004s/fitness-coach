"""
Replace all hardcoded .html hrefs in Django page templates with {% url %} tags.
Run once from backend/: python fix_template_links.py
"""
import os
import re

PAGES_DIR = os.path.join(os.path.dirname(__file__), "templates", "pages")

# Map old href values → Django {% url %} tag
HREF_MAP = {
    'Index.html':                       "{% url 'accounts:home' %}",
    'smartworkoutlog.html':             "{% url 'accounts:workouts' %}",
    'Nutrition &amp; marco tracker.html': "{% url 'accounts:nutrition' %}",
    'Nutrition & marco tracker.html':   "{% url 'accounts:nutrition' %}",
    'body metrixs.html':                "{% url 'accounts:metrics' %}",
    'Ai fitness coach.html':            "{% url 'accounts:ai_coach' %}",
    'pro.html':                         "{% url 'accounts:pro' %}",
    'signin.html':                      "{% url 'accounts:signin' %}",
    'signup.html':                      "{% url 'accounts:signup' %}",
    'logout.html':                      "{% url 'accounts:logout' %}",
}

LOAD_TAG = '{% load static %}\n'

count = 0
files_changed = 0

for fname in os.listdir(PAGES_DIR):
    fpath = os.path.join(PAGES_DIR, fname)
    if not fname.endswith('.html'):
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace href="<old>" with href="{% url ... %}"
    for old, new in HREF_MAP.items():
        pattern = f'href="{re.escape(old)}"'
        replacement = f'href="{new}"'
        matches = len(re.findall(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            count += matches

    # Add {% load static %} at the top if any {% url %} tag was injected
    if content != original:
        # Ensure the Django template engine can find the url tag
        # (url is a built-in tag, no load needed, but we add load static
        #  in case templates use static files later)
        files_changed += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Done — replaced {count} href(s) across {files_changed} file(s).")
