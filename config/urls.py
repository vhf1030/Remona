"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.shortcuts import redirect

from app import views  #

urlpatterns = [
    path('', views.theme_info, name='home'),  # 루트 URL을 테마 정보로 설정
    path('theme_info/', views.theme_info, name='theme_info'),
    path('reserve_info/', views.reserve_info, name='reserve_info'),
]
