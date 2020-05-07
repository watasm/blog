from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('articles', views.ArticleViewSet)
router.register('comments', views.CommentViewSet)
