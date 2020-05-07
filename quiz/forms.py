from django import forms
from django.forms.models import inlineformset_factory
from .models import Question, QuestionChoices, Quiz
from blog.models import Category

QuestionChoicesFormSet = inlineformset_factory(Question, QuestionChoices, fields=['choice', 'is_right_choice'], max_num = 4, extra=4, can_delete=True)

class QuizForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Quiz
        fields = ['category', 'title', 'description', 'image']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = {'question'}

class QuestionAnswerForm(forms.Form):
    def __init__(self, data, question, *args, **kwargs):
        super(QuestionAnswerForm, self).__init__(data, *args, **kwargs)
        #self.fields['choices'] = forms.ChoiceField(choices=[(choice.pk, choice) for choice in choices], widget=forms.RadioSelect)
        self.fields['choice'] = forms.ModelChoiceField(queryset=question.choices.all(), widget=forms.Select)
