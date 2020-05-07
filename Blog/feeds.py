from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Article

class LatestArticlesFeed(Feed):
    title = 'My blog'
    link = '/'
    description = 'New posts of my blog.'

    def items(self):
        return Article.objects.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.description, 30)
