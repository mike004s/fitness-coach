"""
End-to-end smoke tests for auth flow and page navigation.
Run with:  python test_e2e.py
"""
import requests

BASE = "http://127.0.0.1:8000"
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name, ok, detail=""):
    tag = PASS if ok else FAIL
    results.append(ok)
    print(f"  [{tag}] {name}" + (f"  ({detail})" if detail else ""))


print("\n=== KINETIC End-to-End Tests ===\n")

s = requests.Session()

# ── 1. Unauthenticated redirect ──────────────────────────────────────────
print("[1] Unauthenticated access → redirect to signin")
r = s.get(f"{BASE}/", allow_redirects=False)
check("GET / redirects", r.status_code in (301, 302), f"status={r.status_code}")
check("Redirects to signin", "/accounts/signin/" in r.headers.get("Location", ""), r.headers.get("Location", ""))

# ── 2. Protected pages redirect when not logged in ───────────────────────
print("\n[2] Protected pages redirect to signin when unauthenticated")
protected = [
    "/workouts/", "/nutrition/", "/metrics/", "/ai-coach/", "/pro/",
    "/Index.html", "/smartworkoutlog.html", "/pro.html",
]
for url in protected:
    r = s.get(f"{BASE}{url}", allow_redirects=False)
    check(f"GET {url} → redirect", r.status_code in (301, 302), f"status={r.status_code}")

# ── 3. Signin page renders ───────────────────────────────────────────────
print("\n[3] Signin page renders for anonymous users")
r = s.get(f"{BASE}/accounts/signin/")
check("Signin page 200", r.status_code == 200)
check("Contains email field", "mail" in r.text.lower() or "email" in r.text.lower())
check("Contains CSRF token", "csrfmiddlewaretoken" in r.text)

# ── 4. Signup page renders ───────────────────────────────────────────────
print("\n[4] Signup page renders for anonymous users")
r = s.get(f"{BASE}/accounts/signup/")
check("Signup page 200", r.status_code == 200)
check("Contains password field", "password" in r.text.lower())

# ── 5. Signup flow ───────────────────────────────────────────────────────
print("\n[5] Signup a new user")
# Get CSRF token from signup page
r = s.get(f"{BASE}/accounts/signup/")
import re
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
token = csrf.group(1) if csrf else ""
check("Got CSRF token", bool(token))

data = {
    "csrfmiddlewaretoken": token,
    "full_name": "Test User",
    "email": "testuser@kinetic.app",
    "password1": "KineticStrong99!",
    "password2": "KineticStrong99!",
}
r = s.post(f"{BASE}/accounts/signup/", data=data, allow_redirects=True)
check("Signup succeeded (redirect to home)", r.status_code == 200)
check("Landed on authenticated page", "KINETIC" in r.text)

# ── 6. Authenticated access to protected pages ──────────────────────────
print("\n[6] Authenticated access to protected pages")
for url in ["/", "/workouts/", "/nutrition/", "/metrics/", "/ai-coach/", "/pro/"]:
    r = s.get(f"{BASE}{url}")
    check(f"GET {url} → 200", r.status_code == 200, f"status={r.status_code}")

# ── 7. Legacy .html routes work when authenticated ───────────────────────
print("\n[7] Legacy .html routes work when authenticated")
for url in ["/Index.html", "/smartworkoutlog.html", "/pro.html"]:
    r = s.get(f"{BASE}{url}")
    check(f"GET {url} → 200", r.status_code == 200, f"status={r.status_code}")

# ── 8. Logout flow ──────────────────────────────────────────────────────
print("\n[8] Logout flow")
r = s.get(f"{BASE}/accounts/logout/")
check("Logout page 200", r.status_code == 200)
check("Shows disconnect form", "csrfmiddlewaretoken" in r.text or "Terminate" in r.text)

# POST logout
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
token = csrf.group(1) if csrf else ""
r = s.post(f"{BASE}/accounts/logout/", data={"csrfmiddlewaretoken": token}, allow_redirects=True)
check("Logout redirect to signin", r.status_code == 200 and ("Welcome Back" in r.text or "signin" in r.url))

# Verify we're logged out
r = s.get(f"{BASE}/workouts/", allow_redirects=False)
check("After logout, protected page redirects", r.status_code in (301, 302))

# ── 9. Login flow ────────────────────────────────────────────────────────
print("\n[9] Login with created user")
r = s.get(f"{BASE}/accounts/signin/")
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
token = csrf.group(1) if csrf else ""
data = {
    "csrfmiddlewaretoken": token,
    "username": "testuser@kinetic.app",
    "password": "KineticStrong99!",
}
r = s.post(f"{BASE}/accounts/signin/", data=data, allow_redirects=True)
check("Login succeeded", r.status_code == 200)
check("Landed on home page", "KINETIC" in r.text)

# ── 10. Google OAuth link present ────────────────────────────────────────
print("\n[10] Google OAuth link present")
s2 = requests.Session()  # fresh anonymous session
r = s2.get(f"{BASE}/accounts/signin/")
check("Google login link", "/accounts/google/login/" in r.text)

# ── Summary ──────────────────────────────────────────────────────────────
passed = sum(results)
total = len(results)
print(f"\n{'='*50}")
print(f"  Results: {passed}/{total} passed")
if passed == total:
    print(f"  \033[92mAll tests passed!\033[0m")
else:
    print(f"  \033[91m{total - passed} test(s) failed.\033[0m")
print(f"{'='*50}\n")
