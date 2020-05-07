from rest_framework import routers
from .views import QuizViewSet
from .views import QuestionViewSet

router = routers.DefaultRouter()
router.register('quizzes', QuizViewSet)
router.register('questions', QuestionViewSet)
