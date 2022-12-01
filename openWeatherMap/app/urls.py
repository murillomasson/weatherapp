from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # User Authentication
    path('registeruser/', views.registeruser, name="register_user"),
    path('loginuser/', views.loginuser, name="login_user"),
    path('logoutuser/', views.logoutuser, name="logout_user"),

    # Use login main window
    path('delete/<name>/', views.delete, name='delete'),
    path('main/', views.mainpage, name="main"),

]
