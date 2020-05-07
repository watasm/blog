from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('list/', views.QuizListView.as_view(), name='quiz_list'),
    path('list/<slug>/', views.QuizListView.as_view(), name='quiz_list_by_category'),
    path('detail/<pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quiz/create/', views.QuizCreateUpdateView.as_view(), name='quiz_create'),
    path('<id>', views.QuizCreateUpdateView.as_view(), name='quiz_update'),
    path('<quiz_id>/question/create/', views.QuizQuestionCreateUpdateView.as_view(), name='quiz_questions_create'),
    path('<quiz_id>/question/<id>/', views.QuizQuestionCreateUpdateView.as_view(), name='quiz_questions_update'),
    path('<id>/take/', views.take_quiz, name='take_quiz'),
    path('ajax/recive_user_answer', views.recive_user_answer, name='recive_user_answer'),
    path('ajax/get_next_question', views.get_next_question, name='get_next_question'),
    path('ajax/add_quiz_to_profile', views.add_quiz_to_profile, name='add_quiz_to_profile'),
    path('test_new_quiz/<id>/', views.test_new_quiz, name='test_new_quiz'),
    #path('ajax/check_user_answers', views.check_user_answers, name='check_user_answers'),
    path('results/', views.check_and_display_user_answers, name='check_and_display_user_answers'),
    path('edit/', views.quiz_create_update, name='quiz_create_update')
]
