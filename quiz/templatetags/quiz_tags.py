from django import template
from ..models import Question, QuestionChoices
from random import shuffle

register = template.Library()

@register.inclusion_tag('quiz/question_choices_section.html')
def get_choices(question):
    choices = list(question.choices.all())
    shuffle(choices)
    return {'choices': choices, 'question_id': question.id}
