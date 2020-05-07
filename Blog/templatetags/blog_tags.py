from django import template
from ..models import Article
from django.db.models import Count
from accounts.models import Preference
from accounts.forms import SignupForm

register = template.Library()

@register.inclusion_tag('blog/preferences.html')
def get_preferences():
    preferences = Preference.objects.all()
    return {'preferences' : preferences}

@register.inclusion_tag('blog/most_commented_articles.html')
def get_most_commented_articles(count = 5):
    most_commented_articles = Article.objects.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
    return {'most_commented_articles': most_commented_articles}

@register.inclusion_tag('blog/most_liked_articles.html')
def get_most_liked_articles(count = 5):
    most_liked_articles = Article.objects.annotate(total_likes=Count('like')).order_by('-total_likes')[:count]
    return {'most_liked_articles': most_liked_articles}

# @register.inclusion_tag('blog/popular_articles_section.html')
# def get_popular_articles(count = 4):
#     popular_articles = Article.objects.annotate(total_likes=Count('like'), total_comments=Count('comments')).order_by('-total_likes', '-total_comments')[:count]
#     return {'popular_articles': '123456789'}
