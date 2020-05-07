from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from .models import ChatContact, Message, Group
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.apps import apps
from django.db.models import Q, Count

from .forms import GroupCreateForm, GroupAddUsersForm
from django.db.models import Prefetch, Max

from django.http import JsonResponse

from django.contrib.auth.models import User

from datetime import datetime


class Chat(LoginRequiredMixin, TemplateResponseMixin, View):
    groups = None
    conversations = None
    model = None
    object = None
    template_name = 'chat/chat.html'


    def get(self, request, model_name=None, id=None):
        if id:
            try:
                if model_name == 'conversation':
                    self.object = ChatContact.objects.select_related('user_to', 'user_from', 'user_to__profile', 'user_from__profile')\
                    .only('user_from__id', 'user_from__first_name', 'user_from__last_name', 'user_to__id', 'user_to__first_name', 'user_to__last_name', 'user_to__profile__image').get(id=id)

                elif model_name == 'group':
                    self.object = Group.objects.prefetch_related('participants', 'participants__profile')\
                    .only('participants__id', 'participants__first_name', 'participants__last_name', 'participants__profile__image').get(id=id)

                else:
                    raise Exception()

            except:
                return HttpResponseNotFound()

            if model_name == 'group':
                if not request.user in self.object.participants.all():
                    return HttpResponseForbidden()
            else:
                if self.object.user_from != request.user and self.object.user_to != request.user:
                    return HttpResponseForbidden()

        #last messages ids of even group
        message_ids = Message.objects.values('group').annotate(max_id=Max('id')).values_list('max_id')

        self.groups = Group.objects.prefetch_related(Prefetch('messages', queryset=Message.objects.select_related('user').prefetch_related('content')\
        .only('user__id', 'user__first_name', 'user__last_name')\
        .filter(id__in=message_ids), to_attr='last_message')).filter(participants=request.user)

        #last messages ids of even conversation
        message_ids = Message.objects.values('chatcontact').annotate(max_id=Max('id')).values_list('max_id')

        self.conversations = ChatContact.objects.select_related('user_to', 'user_from', 'user_to__profile', 'user_from__profile', 'user_to__onlineuseractivity', 'user_from__onlineuseractivity')\
        .only('user_from__id', 'user_from__first_name', 'user_from__last_name', 'user_to__id', 'user_to__first_name', 'user_to__last_name')\
        .prefetch_related(Prefetch('messages', queryset=Message.objects.select_related('user').prefetch_related('content')\
        .filter(id__in=message_ids), to_attr='last_message')).filter(Q(user_from=request.user, status='F') | Q(user_to=request.user, status='F'))
        return render(request, 'chat/chat.html', {'model_name': model_name, 'chat': self.object, 'groups': self.groups, 'conversations': self.conversations})

def create_group(request):
    if request.method == 'POST':
        group_create_form = GroupCreateForm(data=request.POST, user=request.user)
        if group_create_form.is_valid():
            new_group = Group.objects.create()
            new_group.participants.add(request.user.id)
            for id in group_create_form.cleaned_data['participants']:
                new_group.participants.add(int(id))
            return redirect(reverse('chat:chat', args=['group', new_group.id]))

    else:
        group_create_form = GroupCreateForm(user=request.user)

    return render(request, 'chat/group_create.html', {'group_create_form': group_create_form})

def leave_from_group(request, id):
    group = Group.objects.only('participants').prefetch_related('participants').get(id=id)
    if request.user in group.participants.all():
        group.participants.remove(request.user)
    else:
        return HttpResponseForbidden()
    return redirect(reverse('chat:chat_list'))

def add_users_to_group(request, id):
    try:
        group = Group.objects.prefetch_related('participants').get(id=id)
    except:
        return HttpResponseNotFound()

    candidates = (request.user.user_friends.all() | request.user.friends.all()).difference(group.participants.all())
    if request.method == 'POST':
        form = GroupAddUsersForm(data=request.POST, candidates=candidates)
        if form.is_valid():
            for id in form.cleaned_data['candidates']:
                group.participants.add(int(id))
            return redirect(reverse('chat:chat', args=['group', group.id]))

    else:
        form = GroupAddUsersForm(candidates=candidates)
    num_of_candidates = len(candidates)
    return render(request, 'chat/add_users_to_group.html', {'group': group, 'form': form, 'num_of_candidates': num_of_candidates})

def get_next_message_packet(request):
    if request.is_ajax():
        model_name = request.GET.get('model_name')
        chat_id = request.GET.get('chat_id')
        first_message_date = request.GET.get('first_message_date')
        first_message_date = datetime.strptime(first_message_date, "%Y-%m-%dT%H:%M:%S.%fZ")

        packet_size = 11

        if model_name == 'group/':
            messages = Message.objects.select_related('user', 'user__profile').defer('user__password', 'user__username', 'user__email')\
            .prefetch_related('content').filter(group__id=chat_id).order_by('-id')[:packet_size][::-1]
        elif model_name == 'conversation/':
            messages = Message.objects.select_related('user', 'user__profile').defer('user__password', 'user__username', 'user__email')\
            .prefetch_related('content').filter(chatcontact__id=chat_id, date__lt=first_message_date).order_by('-id')[:packet_size][::-1]
        else:
            return JsonResponse({'status': 'ko'})

        data = []
        end = False
        if len(messages) != packet_size:
            end = True
            index = None
        else:
            index = 0

        for message in messages[:index:-1]:
            content_type = message.content_type.model_class().__name__
            if content_type == 'Image':
                content = message.content.image.url
            else:
                content = message.content.text
            temp = {
                'content_type': content_type,
                'content': content,
                'user_id': message.user.id,
                'user_image_url': message.user.profile.get_image_url(),
                'date': message.date
            }

            data.append(temp)
        return JsonResponse({'messages': data, 'end': end})
