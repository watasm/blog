from rest_framework import routers
from .views import UserViewSet, PreferenceViewSet, ProfileViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('preferences', PreferenceViewSet)
router.register('profiles', ProfileViewSet)
