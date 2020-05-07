import asyncio
import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from blog.models import Article, Comment
from datetime import datetime
from channels.exceptions import StopConsumer
from accounts.models import Profile

class CommentConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("Websocket connect event", event)
        await self.send({
            'type': 'websocket.accept'
        })

        radis_article_id = self.scope["url_route"]["kwargs"]["id"]
        self.article = 'article_' + str(radis_article_id)
        print(self.article)
        await self.channel_layer.group_add(
            self.article,
            self.channel_name,
        )

    async def websocket_disconnect(self, event):
        print("Websocket disconnect event", event)
        await self.send({
            'type': 'websocket.close'
        })
        radis_article_id = self.scope["url_route"]["kwargs"]["id"]
        self.article = 'article_' + str(radis_article_id)
        await self.channel_layer.group_discard(
            self.article,
            self.channel_name,
        )
        raise StopConsumer()


    async def websocket_receive(self, event):

        comment = event.get('text')
        new_comment = json.loads(comment)

        user = self.scope["user"]

        article_id = self.scope["url_route"]["kwargs"]["id"]
        article = await self.get_article(article_id)

        comment_text = new_comment['comment_text']
        new_object = await self.create_comment(user, article, comment_text)

        user_image_url = await self.get_user_image_url(user.id)

        radis_comment = {
            'comment_text':str(new_object.text),
            'user': str(new_object.user.get_full_name()),
            'post_date': str(new_object.post_date),
            'like': str(0),
            'id': str(new_object.id),
            'user_image_url': user_image_url

        }

        await self.channel_layer.group_send(
            self.article,
            {
                'type': 'show_comment',
                'text': json.dumps(radis_comment),
            }
        )

    @database_sync_to_async
    def get_user_image_url(self, user_id):
        p = Profile.objects.defer('preferences', 'passed_quizzes', 'user', 'is_subscribed_to_the_newsletter').filter(user__id=user_id)
        return p[0].get_image_url()

    @database_sync_to_async
    def get_article(self, article_id):
        return Article.objects.get(id = article_id)

    @database_sync_to_async
    def create_comment(self, user, article, comment_text):
        new_comment = Comment.objects.create(user=user, article=article, text = comment_text)
        return new_comment

    async def show_comment(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text'],
        })
