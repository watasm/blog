from django.contrib.auth.models import User
from django import forms
from blog.models import Article, Category, Comment
from datetime import datetime
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django.contrib.auth.password_validation import validate_password

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=('name', )

class ArticleForm(forms.ModelForm):
    title = forms.CharField(required=True)
    description = forms.CharField(required=True)
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.SelectMultiple, required=True)
    text = forms.CharField(widget=SummernoteWidget(), required=True)

    field_order = ['title', 'description', 'category','tags', 'text']
    class Meta:
        model = Article
        fields = {'title', 'description', 'category', 'tags', 'text'}

class ArticleUpdateForm(forms.ModelForm):
    text = forms.CharField(widget=SummernoteWidget())
    class Meta:
        model=Article
        fields=('title','description', 'text', 'category', 'tags')

class CommentForm(forms.ModelForm):
    field_order = ['text']
    class Meta:
        model=Comment
        fields=('text',)


class EmailArticleForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget = forms.Textarea)

class SearchForm(forms.Form):
    query = forms.CharField()
