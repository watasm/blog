from rest_framework import viewsets
from quiz.models import Quiz, Question, QuestionChoices, QuestionAnswer

from .serializers import QuizSerializer, QuestionSerializer, QuestionChoicesSerializer

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from Blog.permissions import IsOwnerOrReadOnly
from .permissions import IsQuizOwnerOrReadOnly

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('user').prefetch_related('category', 'questions', 'questions__choices').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsQuizOwnerOrReadOnly]
