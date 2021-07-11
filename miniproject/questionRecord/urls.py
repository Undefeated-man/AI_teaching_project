from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views


urlpatterns = [
    # 微信小程序登录
    # 微信登录页面userinfo
    path('userinfo', views.userinfo),
]
