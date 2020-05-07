from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

from .utility import encrypt_image_name

class Message(models.Model):
    user = models.ForeignKey(User, related_name='user_messages', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in':('text','video','image','file')})
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()

class ContentBase(models.Model):

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)

    def render(self):
        pass

class Text(ContentBase):
    text = models.TextField()

    def render(self):
        return self.text

class File(ContentBase):
    file = models.FileField(upload_to='files')

    def render(self):
        return self.file.url


class Image(ContentBase):
    image = models.ImageField('image', upload_to=encrypt_image_name)

    def render(self):
        return self.image.url

class Video(ContentBase):
    url = models.URLField()

    def render(self):
        return self.url

class BaseChat(models.Model):
    messages = models.ManyToManyField(Message, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}".format(self.pk)

    def get_next_message_packet(self):
        return self.messages.order_by('-date')[:20][::-1]


STATUS_CHOICES = (
    ('F', 'friends'),
    ('PF', 'pending_first_second'),
    ('PS', 'pending_second_first'),
    # ('BF', 'block_first_second'),
    # ('BS', 'block_second_first'),
    # ('BB', 'block_both'),
)

class ChatContact(BaseChat):
    user_from = models.ForeignKey(User, related_name='friend_request_from', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='friend_request_to', on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, null=True)

    class Meta:
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return '{}_{}_{}'.format(self.user_from, self.status, self.user_to)

User.add_to_class('friends', models.ManyToManyField('self', through=ChatContact, related_name='user_friends', symmetrical=False, blank=True))

class Group(BaseChat):
    participants = models.ManyToManyField(User, related_name='chats', blank=True)
