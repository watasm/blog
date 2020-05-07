from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.Chat.as_view(), name = 'chat_list'),
    path('<str:model_name>/<int:id>/', views.Chat.as_view(), name = 'chat'),
    path('group/create/', views.create_group, name='create_group'),
    path('ajax/get_next_message_packet/', views.get_next_message_packet, name='get_next_message_packet'),
    path('leave/group/<int:id>/', views.leave_from_group, name='leave_from_group'),
    path('group/<int:id>/add_users_to_group/', views.add_users_to_group, name='add_users_to_group')
]
