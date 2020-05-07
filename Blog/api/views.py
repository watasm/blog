from blog.models import Category, Article, Comment
from .serializers import CategorySerializer, ArticleSerializer, CommentSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from Blog.permissions import IsOwnerOrReadOnly, IsAdminUserOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('user').prefetch_related('tags', 'category', 'like', 'comments', 'comments__user', 'comments__comment_likes').all()\
    .defer('user__password', 'user__username', 'user__email', 'user__last_login', 'user__is_superuser', 'user__is_staff', 'user__is_active', 'user__date_joined')

    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user').prefetch_related('comment_likes').all()\
    .defer('user__password', 'user__username', 'user__email', 'user__last_login', 'user__is_superuser', 'user__is_staff', 'user__is_active', 'user__date_joined')

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
