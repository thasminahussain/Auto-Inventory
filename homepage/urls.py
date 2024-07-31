from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.email_verification, name='verify-email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'), 
    path('about/', views.AboutView.as_view(), name='about'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('registration/', views.register, name='registration'),  
    path('forgot-password/', views.forgot_password, name='forgot-password'),  
    path('password-reset/', views.password_reset, name='password-reset'),  
    path('reset-password/', views.reset_password, name='reset-password'),  
    path('generate-report/', views.GenerateReportView.as_view(), name='generate-report'),
    path('under-work/', views.UnderWorkView.as_view(), name='under-work'),
]