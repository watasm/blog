from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from blog.consumers import CommentConsumer
from chat.consumers import ChatConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/articles/<int:id>", CommentConsumer),
                path('ws/chat/<model_name>/<int:id>/', ChatConsumer),
                path('ws/chat/<model_name>/<int:id>/', ChatConsumer),
            ])
        )
    )
})
