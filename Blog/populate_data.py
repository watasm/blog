from django.contrib.auth.models import User
from blog.models import Category
import random
from blog.models import Article
from faker import Faker

fake = Faker()
users = User.objects.all()
categories = Category.objects.all()
original_tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7']

t = 'Title'

def add_articles():
    for i in range(1,201):
        user = random.choice(users)
        category = fake.random_choices(categories)
        tags = fake.random_choices(original_tags)
        title = t + str(i)
        text = fake.text(10000)
        description = text[:100]
        article = Article.objects.create(user=user, title=title, text=text, description=description)

        for c in category:
            article.category.add(c)

        for tag in tags:
            article.tags.add(tag)

add_articles()
