from django.urls import path, include
from . import views
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap
from .feeds import LatestArticlesFeed
from blog.forms import ArticleForm

app_name = 'blog'

sitemaps = {
    'articles': ArticleSitemap,
}

urlpatterns = [
    path('', views.article_list, name = 'article_list'),
    path('<slug>', views.article_list, name = 'article_list_by_category'),
    path('article/add', views.add_article, name='add_article'),
    path('article/like', views.like_article, name='like_article'),
    path('comment/like', views.like_comment, name='like_comment'),
    path('category/add', views.add_category, name='add_category'),
    path('articles/<int:id>', views.article_detail, name='article_detail'),
    path('article/edit/<int:pk>', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('article/delete/<int:pk>', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('article/share/<int:pk>', views.article_share, name='article_share'),
    path('schemas/sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('article/feed', LatestArticlesFeed(), name='article_feed'),
    path('article/search', views.article_search, name='article_search'),
    path('ajax/mark_notification_as_read', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('ajax/mark_all_notifications_as_read', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('elasticsearch_results/', views.ElasticSearchView.as_view(), name='elasticsearch_results'),
    path('ajax/add_bookmark', views.add_bookmark, name='add_bookmark')
]
