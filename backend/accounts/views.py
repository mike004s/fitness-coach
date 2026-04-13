from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import Http404

from .forms import SignInForm, SignUpForm


PAGE_TEMPLATE_MAP = {
    'dashboard': 'pages/Index.html',
    'workouts': 'pages/smartworkoutlog.html',
    'nutrition': 'pages/Nutrition & marco tracker.html',
    'metrics': 'pages/body metrixs.html',
    'ai-coach': 'pages/Ai fitness coach.html',
    'pro': 'pages/pro.html',
}


def home(request):
    """Landing page — redirects to dashboard if authenticated, else to signin."""
    if request.user.is_authenticated:
        return render(request, 'pages/Index.html')
    return redirect('accounts:signin')


@require_http_methods(['GET', 'POST'])
def signin_view(request):
    """Email + password login view."""
    if request.user.is_authenticated:
        return redirect('accounts:home')

    form = SignInForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            # Validate next_url is relative to prevent open-redirect
            if not next_url.startswith('/'):
                next_url = '/'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/signin.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def signup_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('accounts:home')

    form = SignUpForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to KINETIC, {user.get_display_name()}!')
            return redirect('accounts:home')

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def logout_view(request):
    """Logout — shows confirmation page on GET, logs out on POST."""
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:signin')
    return render(request, 'accounts/logout.html')


@login_required
def protected_page(request, page_key):
    """Render legacy frontend pages through Django with auth protection."""
    template_name = PAGE_TEMPLATE_MAP.get(page_key)
    if not template_name:
        raise Http404('Page not found.')
    return render(request, template_name)
