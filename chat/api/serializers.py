from ..models import Message, ChatContact, Group
from django.contrib.auth.models import User

from rest_framework import serializers
from accounts.api.serializers import SimpleUserSerializer

class ContentRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()

class MessageSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    content = ContentRelatedField(read_only=True)
    content_type = serializers.IntegerField(min_value=0, write_only=True)
    object_id = serializers.IntegerField(min_value=0, write_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'date', 'content_type', 'object_id']

class ChatContactSerializer(serializers.ModelSerializer):
    user_from = SimpleUserSerializer(read_only=True)
    user_to = SimpleUserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatContact
        exclude = ['status']

class GroupSerializer(serializers.ModelSerializer):
    participants = SimpleUserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'participants', 'messages', 'last_message']

    # def get_fields(self, *args, **kwargs):
    #     fields = super().get_fields(*args, **kwargs)
    #     request = self.context.get('request', None)
    #     if request and request.method in ('list'):
    #         fields['last_message'] = serializers.SerializerMethodField(read_only=True)
    #     elif request.method != 'list':
    #         fields['messages'] = MessageSerializer(many=True, read_only=True)
    #     return fields

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            last_message = last_message.content.render()
            return last_message
        return None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        friends = user.friends.all() | user.user_friends.all()
        self.fields['participants_ids'] = serializers.PrimaryKeyRelatedField(queryset=friends, write_only=True, many=True)


    def create(self, validated_data):
        participants_ids = validated_data.get('participants_ids')
        group = Group.objects.create()

        group.participants.add(self.context['request'].user)
        for participant in participants_ids:
            group.participants.add(participant)

        return group
