from ..models import Message, ChatContact, Group
from rest_framework import viewsets
from .serializers import MessageSerializer, ChatContactSerializer, GroupSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from Blog.permissions import IsOwnerOrReadOnly
from .permissions import IsInGroupOrAdminPermission

from rest_framework.decorators import action

from rest_framework import status
from rest_framework.response import Response

from django.db.models import Q

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Message.objects.select_related('user', 'content_type').prefetch_related('content').filter(user=self.request.user)\
        .defer('user__password', 'user__username', 'user__email', 'user__last_login', 'user__is_superuser', 'user__is_staff', 'user__is_active', 'user__date_joined')

        return queryset

class ChatContactViewSet(viewsets.ModelViewSet):
    queryset = ChatContact.objects.all()
    serializer_class = ChatContactSerializer

    def get_queryset(self):
        queryset = ChatContact.objects.select_related('user_from', 'user_to').prefetch_related('messages', 'messages__user', 'messages__content')\
        .filter(Q(user_from=self.request.user, status='F') | Q(user_to=self.request.user, status='F'))

        return queryset

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated & IsInGroupOrAdminPermission]

    def get_queryset(self):
        return Group.objects.prefetch_related('participants', 'messages', 'messages__user', 'messages__content').filter(participants=self.request.user)

    # if returned all groups
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         self.permission_classes = [IsAuthenticated]
    #
    #     else:
    #         self.permission_classes = [IsAuthenticated & IsInGroupOrAdminPermission]
    #
    #     return super().get_permissions()

    @action(detail=True, methods=['POST'], url_path='leave_group', url_name='leave-group')
    def leave_group(self, request, *args, **kwargs):
        group = self.get_object()
        if request.user in group.participants.all():
            group.participants.remove(request.user)
            return Response({'message': 'You leaved the group'}, status.HTTP_200_OK)
        return Response({'message': 'Not in group'}, status.HTTP_400_BAD_REQUEST)
