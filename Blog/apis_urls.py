from django.urls import path, include

from rest_framework import routers
from blog.api.urls import router as blog_router
from quiz.api.urls import router as quiz_router
from accounts.api.urls import router as accounts_router
from chat.api.urls import router as chat_router

router = routers.DefaultRouter()
router.registry.extend(blog_router.registry)
router.registry.extend(quiz_router.registry)
router.registry.extend(accounts_router.registry)
router.registry.extend(chat_router.registry)

urlpatterns = [
    path('', include(router.urls))
]
