"""Test AI Chat API endpoint and all page routes."""
import requests
import json
import re
import sys

BASE = 'http://127.0.0.1:8000'
passed = 0
failed = 0

def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label}")

def get_csrf_from_html(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else ''

print("=== AI Chat API & Route Tests ===\n")

# --- Auth setup ---
s = requests.Session()
r = s.get(BASE + '/accounts/signin/')
csrf_token = get_csrf_from_html(r.text)
print("[Setup] Login as admin")
r = s.post(BASE + '/accounts/signin/', data={
    'csrfmiddlewaretoken': csrf_token,
    'username': 'admin@kinetic.app',
    'password': 'admin1234',
}, allow_redirects=True)
check("Login succeeded", r.status_code == 200 and 'KINETIC' in r.text and 'Sign In' not in r.text)

# --- Test all page routes ---
print("\n[1] All page routes return 200")
routes = {
    '/': 'Home',
    '/workouts/': 'Workouts',
    '/nutrition/': 'Nutrition',
    '/metrics/': 'Metrics',
    '/ai-coach/': 'AI Coach',
    '/pro/': 'Pro',
}
for path, name in routes.items():
    r = s.get(BASE + path)
    check(f"GET {path} ({name}) → {r.status_code}", r.status_code == 200)

# --- Legacy .html routes ---
print("\n[2] Legacy .html routes")
legacy = ['/Index.html', '/smartworkoutlog.html', '/pro.html']
for path in legacy:
    r = s.get(BASE + path)
    check(f"GET {path} → {r.status_code}", r.status_code == 200)

# --- AI Chat API: workout ---
print("\n[3] AI Chat - workout question")
csrf = s.cookies.get('csrftoken', '')
print(f"    (CSRF present: {bool(csrf)})")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': 'Recommend a 15-min HIIT workout'},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 200", r.status_code == 200)
data = r.json()
check(f"Category is 'workout': {data.get('category')}", data.get('category') == 'workout')
check(f"Reply not empty", len(data.get('reply', '')) > 10)
print(f"    Reply: {data['reply'][:100]}...")

# --- AI Chat API: nutrition ---
print("\n[4] AI Chat - nutrition question")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': 'What should I eat for dinner tonight?'},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 200", r.status_code == 200)
data = r.json()
check(f"Category is 'nutrition': {data.get('category')}", data.get('category') == 'nutrition')
check(f"Has macros", data.get('macros') is not None)
print(f"    Macros: {data.get('macros')}")
print(f"    Reply: {data['reply'][:100]}...")

# --- AI Chat API: form ---
print("\n[5] AI Chat - form question")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': 'How do I fix my squat form?'},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 200", r.status_code == 200)
data = r.json()
check(f"Category is 'form': {data.get('category')}", data.get('category') == 'form')
print(f"    Reply: {data['reply'][:100]}...")

# --- AI Chat API: macro ---
print("\n[6] AI Chat - macro question")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': 'Explain macro tracking and protein intake'},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 200", r.status_code == 200)
data = r.json()
check(f"Category is 'macro': {data.get('category')}", data.get('category') == 'macro')
print(f"    Reply: {data['reply'][:100]}...")

# --- AI Chat API: general ---
print("\n[7] AI Chat - general question")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': 'Hello, how are you?'},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 200", r.status_code == 200)
data = r.json()
check(f"Category is 'general': {data.get('category')}", data.get('category') == 'general')
print(f"    Reply: {data['reply'][:100]}...")

# --- AI Chat API: empty message ---
print("\n[8] AI Chat - empty message (should fail)")
r = s.post(BASE + '/api/ai-chat/',
    json={'message': ''},
    headers={'X-CSRFToken': csrf, 'Content-Type': 'application/json'})
check(f"Status {r.status_code} == 400", r.status_code == 400)
check(f"Error message present", 'error' in r.json())

# --- AI Chat API: unauthenticated ---
print("\n[9] AI Chat - unauthenticated access")
s2 = requests.Session()
r = s2.post(BASE + '/api/ai-chat/',
    json={'message': 'hello'},
    headers={'Content-Type': 'application/json'},
    allow_redirects=False)
check(f"Status {r.status_code} in (302, 403) (auth required)", r.status_code in (302, 403))

# --- AI Chat API: wrong method ---
print("\n[10] AI Chat - GET method (should be 405)")
r = s.get(BASE + '/api/ai-chat/')
check(f"Status {r.status_code} == 405", r.status_code == 405)

# --- Logout ---
print("\n[11] Logout flow")
r = s.get(BASE + '/accounts/logout/')
check(f"Logout page loads", r.status_code == 200)

# --- Summary ---
total = passed + failed
print(f"\n{'='*50}")
print(f"  Results: {passed}/{total} passed")
if failed:
    print(f"  {failed} FAILED")
    sys.exit(1)
else:
    print(f"  All tests passed!")
print(f"{'='*50}")
