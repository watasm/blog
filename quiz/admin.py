from django.contrib import admin
from .models import Quiz, Question, QuestionChoices, QuestionAnswer
# Register your models here.

class QuestionChoicesInline(admin.StackedInline):
    model = QuestionChoices

class QuestionAnswerInline(admin.StackedInline):
    model = QuestionAnswer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionChoicesInline, QuestionAnswerInline]

admin.site.register(Quiz)
admin.site.register(QuestionAnswer)
