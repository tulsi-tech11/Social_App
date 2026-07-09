"""
URL configuration for velora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),

    path('messages/', views.messages, name='messages'),
    path('messages/<int:pk>/', views.messages, name='messages'),
    path('send_msg', views.send_msg, name='send_msg'),
    path('send_msg/<int:pk>/', views.send_msg, name='send_msg'),

    path('create/', views.create, name='create'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('following/', views.following, name='following'),
    path('follow_unfollow/<int:pk>', views.follow_unfollow, name='follow_unfollow'),
    path('followers/', views.followers, name='followers'),
    path('remove/<int:pk>', views.remove, name='remove'),
    path('notification/', views.notification_view, name='notification'),
    path('like_dislike/<int:pk>',views.like_dislike_view, name='like_dislike'),
    path('create-reel/', views.create_reel, name='create_reel'),
    path('reels/', views.reels, name='reels'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('api/unread-counts/', views.get_unread_counts, name='get_unread_counts'),
    path('delete-search-history/<int:pk>/', views.delete_search_history, name='delete_search_history'),
    path('add-to-search-history/<int:pk>/', views.add_to_search_history, name='add_to_search_history'),
    path('user-profile/<int:pk>/', views.user_profile, name='user_profile'),
    path('add_comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('get_comments/<int:pk>/', views.get_comments, name='get_comments'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)