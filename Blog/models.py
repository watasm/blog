from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse
from taggit.managers import TaggableManager

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Category', db_index=True, unique=True)
    slug = models.SlugField(max_length=100, db_index=True, unique=True)
    not_sended = models.BooleanField(default = False)

    class Meta:
        ordering=['name']

    def get_absolute_url(self):
        return reverse('blog:article_list_by_category', args=[str(self.slug)])

    def __str__(self):
        return self.name

class MathManager(models.Manager):
    def get_queryset(self):
        return super(MathManager, self).get_queryset().filter(category = 2)

class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article', blank=False)
    category = models.ManyToManyField(Category)
    tags = TaggableManager()
    title = models.CharField(max_length=100, verbose_name='Title')
    image = models.ImageField('image', upload_to='blog/articles/images', blank=True)
    description = models.CharField(max_length=450, verbose_name='Description')
    text = models.TextField(verbose_name='Text')
    like = models.ManyToManyField(User, related_name='likes', blank = True)
    post_date = models.DateTimeField(auto_now=True, verbose_name='Post Date')

    objects = models.Manager()
    math = MathManager()

    class Meta:
        ordering = ('-post_date', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article_detail', args=[str(self.id)])

    def total_likes(self):
        return self.like.count()

    def get_image_url(self):
        if not self.image:
            return '/static/default_images/article_default_image.jpg'
        return self.image.url

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    post_date=models.DateTimeField(default=datetime.now, verbose_name='Post Date')
    comment_likes=models.ManyToManyField(User, related_name='comment_likes', blank = True)

    def __str__(self):
        return self.text[:20]

    def total_likes(self):
        return self.comment_likes.count()

class Bookmark(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="bookmarks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_articles')
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('article', 'user')
