from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from blog.models import Category
from .fields import OrderField

class Quiz(models.Model):
    user = models.ForeignKey(User, related_name='created_quizzes', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='quizzes', on_delete=models.CASCADE, blank=False)
    title = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField('image', upload_to='quiz/images/', blank=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

    def get_absoulte_url(self):
        return reverse('quiz_detail', kwargs={'pk': self.pk})

    def get_image_url(self):
        if not self.image:
            return '/static/default_images/quiz_default_image.jpg'
        return self.image.url

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question = models.TextField()
    order = OrderField(for_fields=['quiz'])

    def __str__(self):
        return self.question

class QuestionChoices(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)
    is_right_choice = models.BooleanField()

    class Meta:
        unique_together = ['question', 'choice']

    def __str__(self):
        return self.choice

class QuestionAnswer(models.Model):
    user = models.ForeignKey(User, related_name='user_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    is_right = models.BooleanField()

    class Meta:
        unique_together = ['user', 'question']
