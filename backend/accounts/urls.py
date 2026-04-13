from django.urls import path
from . import views
from .ai_coach import ai_chat

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/ai-chat/', ai_chat, name='ai_chat_api'),
    path('accounts/signin/', views.signin_view, name='signin'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('workouts/', views.protected_page, {'page_key': 'workouts'}, name='workouts'),
    path('nutrition/', views.protected_page, {'page_key': 'nutrition'}, name='nutrition'),
    path('metrics/', views.protected_page, {'page_key': 'metrics'}, name='metrics'),
    path('ai-coach/', views.protected_page, {'page_key': 'ai-coach'}, name='ai_coach'),
    path('pro/', views.protected_page, {'page_key': 'pro'}, name='pro'),
    # Legacy HTML aliases to keep existing navigation links working
    path('Index.html', views.protected_page, {'page_key': 'dashboard'}, name='legacy_dashboard'),
    path('smartworkoutlog.html', views.protected_page, {'page_key': 'workouts'}, name='legacy_workouts'),
    path('Nutrition & marco tracker.html', views.protected_page, {'page_key': 'nutrition'}, name='legacy_nutrition'),
    path('body metrixs.html', views.protected_page, {'page_key': 'metrics'}, name='legacy_metrics'),
    path('Ai fitness coach.html', views.protected_page, {'page_key': 'ai-coach'}, name='legacy_ai_coach'),
    path('pro.html', views.protected_page, {'page_key': 'pro'}, name='legacy_pro'),
    path('signin.html', views.signin_view, name='legacy_signin'),
    path('signup.html', views.signup_view, name='legacy_signup'),
    path('logout.html', views.logout_view, name='legacy_logout'),
]
