from rest_framework import viewsets
from django.contrib.auth.models import User
from ..models import Preference, Profile
from .serializers import UserSerializer, PreferenceSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from Blog.permissions import IsAdminUserOrReadOnly, IsUserOrAdmin, IsOwnerOrAdminUser

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('profile').prefetch_related('friends', 'following', 'profile__preferences', 'profile__passed_quizzes').all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]

        else:
            self.permission_classes = [IsUserOrAdmin]

        return super().get_permissions()

class PreferenceViewSet(viewsets.ModelViewSet):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').only('id', 'preferences', 'image', 'passed_quizzes', 'is_subscribed_to_the_newsletter', 'user__id')\
    .prefetch_related('passed_quizzes', 'preferences').all()

    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrAdminUser]
