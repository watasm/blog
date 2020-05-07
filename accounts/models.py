from django.db import models
from django.contrib.auth.models import User
import uuid
from quiz.models import Quiz

class Preference(models.Model):
    name = models.CharField(max_length=50, verbose_name='Preference', unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, related_name = 'profile', on_delete = models.CASCADE)
    preferences = models.ManyToManyField(Preference, blank=True, related_name = "profile")
    image = models.ImageField('image', upload_to='blog/images', default='', blank=True)
    passed_quizzes = models.ManyToManyField(Quiz, related_name='profiles', blank=True)
    is_subscribed_to_the_newsletter = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['id']

    def __str__(self):
        return str(self.user)

    def get_image_url(self):
        if not self.image:
            return '/static/default_images/user_default_image.png'
        return self.image.url

class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name="user_from", on_delete = models.CASCADE)
    user_to = models.ForeignKey(User, related_name="user_to", on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return str(self.user_from) + ' follows ' + str(self.user_to)

User.add_to_class('following', models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False, blank=True))
