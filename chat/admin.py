from django.contrib import admin
from .models import ChatContact, Message, Group, Text, Image

admin.site.register(ChatContact)
admin.site.register(Message)
admin.site.register(Group)

admin.site.register(Text)
admin.site.register(Image)
