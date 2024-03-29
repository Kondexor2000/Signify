"""
URL configuration for signify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from signifyapp import views


urlpatterns = [
    path('login/', views.login_existing, name='login_existing'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout_existing'),
    path('notifications/', views.check_payment_deadline, name='notifications'),
    path('records/', views.display_records_with_average_above_10, name='records'),
    path('', views.index, name='index'),
]