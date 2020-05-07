from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ChatContact, Group, Text, Image
import json

import base64
from django.core.files.base import ContentFile

from accounts.models import Profile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['id']
        self.model_name = self.scope['url_route']['kwargs']['model_name']
        self.room_group_name = '{}_{}'.format(self.model_name, self.chat_id)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        message_type = data['message_type']
        user = self.scope['user']
        user_id = user.id
        user_full_name = user.get_full_name()
        user_image_url = await self.get_user_image_url(user.id)

        created_message = await self.create_message(user, message, message_type)

        response_data = {
            'type': 'chat.message',
            'message': message,
            'message_type': message_type,
            'user_id': user_id,
            'user_full_name': user_full_name,
            'user_image_url': user_image_url,
            'chat_id': self.chat_id,
            'model_name': self.model_name
        }

        if message_type == 'image':
            response_data['message_image_url'] = created_message.content.image.url

        # Send message to room group
        await self.channel_layer.group_send(self.room_group_name, response_data)

    @database_sync_to_async
    def get_user_image_url(self, user_id):
        p = Profile.objects.defer('preferences', 'passed_quizzes', 'user', 'is_subscribed_to_the_newsletter').filter(user__id=user_id)
        return p[0].get_image_url()

    @database_sync_to_async
    def create_message(self, user, message, message_type):
        if message_type == 'image':
            format, imgstr = message.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            content = Image.objects.create(image=image)

        elif message_type == 'text':
            content = Text.objects.create(text=message)

        message = Message.objects.create(user=user, content=content)

        if self.model_name == 'group':
            chat = get_object_or_404(Group, id=self.chat_id)
        else:
            chat = get_object_or_404(ChatContact, id=self.chat_id, status='F')
        chat.messages.add(message)
        return message

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        message_type = event['message_type']
        user_id = event['user_id']
        user_full_name = event['user_full_name']
        user_image_url = event['user_image_url']
        chat_id = event['chat_id']
        model_name = event['model_name']

        response_data = {
            'message': message,
            'message_type': message_type,
            'user_id': user_id,
            'user_full_name': user_full_name,
            'user_image_url': user_image_url,
            'chat_id': chat_id,
            'model_name': model_name
        }

        if message_type == 'image':
            message_image_url = event['message_image_url']
            response_data['message_image_url'] = message_image_url

        # Send message to WebSocket
        await self.send(text_data=json.dumps(response_data))
