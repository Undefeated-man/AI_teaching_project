from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views,audioRecognize


urlpatterns = [
    # 微信小程序登录
    # 微信登录页面userinfo
    path('userinfo', views.userinfo),
    url(r"^$", views.upload),
    url(r"^welcome/$", audioRecognize.welcome),
    url(r"^getUserInformation/$",views.getUserInformation),
    url(r"^getRankWithLevel/$", views.getRankWithLevel),
    url(r"^getRankWithoutLevel/$", views.getRankWithoutLevel),
    url(r"^getNewQuestion/$", views.getNewQuestion),
    url(r"^getOneQuesiton/$", views.getOneQuesiton),
    url(r"^getWrongQuestion/$", views.getWrongQuestion),
    url(r"^getNotesCollection/$", views.getNotesCollection),
    url(r"^getHistory/$", views.getHistory),
    url(r"^toCollect/$", views.toCollect),
    url(r"^toCancelCollect/$", views.toCancelCollect),
    url(r"^judgeAnswer/$", views.judgeAnswer),
    url(r"^getUserRank/$", views.getUserRank),
    url(r"^textToSpeechCN/$", views.textToSpeechCN),
    url(r"^recognize$", audioRecognize.recognize, name="recognize"),
]
