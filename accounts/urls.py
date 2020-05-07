from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('edit/', views.user_edit, name='user_edit'),
    path('<int:id>/', views.profile, name='profile'),
    path('follow_user/', views.profile_follow, name='profile_follow'),
    path('list/', views.user_list, name='users'),
    path('signup/', views.CustomSignupView.as_view(), name='signup'),
    path('unsubscribe_from_newsletter/', views.unsubscribe_from_newsletter, name='unsubscribe_from_newsletter'),
    path('add_to_friends/', views.add_to_friends, name='add_to_friends'),
    path('ajax/get_user_friends/', views.get_user_friends, name='ajax_get_user_friends'),
    path('ajax/get_user_articles/', views.get_user_articles, name='ajax_get_user_articles')
]
