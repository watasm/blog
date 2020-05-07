from rest_framework import routers
from .views import MessageViewSet, GroupViewSet, ChatContactViewSet

router = routers.DefaultRouter()
router.register('messages', MessageViewSet, basename='message')
router.register('conversations', ChatContactViewSet, basename='chatcontact')
router.register('groups', GroupViewSet, basename='group')
