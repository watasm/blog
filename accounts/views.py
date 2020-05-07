from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, ProfileCreateUpdateForm, UserUpdateForm, PreferenceForm, CustomSignupForm
from django.contrib.auth.models import User
from .models import Profile, Contact
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models.signals import post_save, m2m_changed
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotFound
from blog.models import Article
from allauth.account.views import SignupView

# added send_email_confirmation to celery tasks
from Blog.celery import app
from allauth.account.utils import send_email_confirmation
send_email_confirmation = app.task(send_email_confirmation)

from chat.models import ChatContact
from notifications.signals import notify
from django.db.models import Q

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

import base64
from django.core.files.base import ContentFile
from uuid import uuid4

from Blog.decorators import ajax_required, debugger_queries
from django.core.cache import cache
from math import ceil


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def get(self, *args, **kwargs):
        form = self.get_form(self.form_class)
        profile_form = ProfileCreateUpdateForm()
        return self.render_to_response(self.get_context_data(form=form, profile_form=profile_form))

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            form = CustomSignupForm(request.POST)
            profile_form = ProfileCreateUpdateForm(request.POST)
            image_base64 = request.POST.get('image')

            try:
                format, imgstr = image_base64.split(';base64,')
            except:
                image = None
            else:
                ext = format.split('/')[-1]
                name = uuid4().hex + '.'
                image = ContentFile(base64.b64decode(imgstr), name=name + ext)

            if form.is_valid() and profile_form.is_valid():
                return self.form_valid(form, profile_form, image)

            return JsonResponse({'status': "400 Bad Request", 'status_code': 400, 'form_errors': form.errors, 'profile_form_errors': profile_form.errors})

        else:
            profile_form = ProfileCreateUpdateForm(request.POST, request.FILES)
            form = self.get_form(self.form_class)
            if form.is_valid() and profile_form.is_valid():
                return self.form_valid(form, profile_form)
            else:
                return self.form_invalid(form, profile_form)

            return self.render_to_response(self.get_context_data(form = form, profile_form=profile_form))


    def form_valid(self, form, profile_form, image=None):
        response = super(CustomSignupView, self).form_valid(form)
        new_profile = profile_form.save(commit = False)
        new_profile.user = self.user
        if image:
            new_profile.image = image

        new_profile.save()
        profile_form.save_m2m()

        if self.request.is_ajax():
            return JsonResponse({'status': "201 Created",  'status_code': 201, 'success_url': '/accounts/confirm-email/'}, status='201')

        return response

    def form_invalid(self, form, profile_form):
        return self.render_to_response(self.get_context_data(form = form, profile_form=profile_form))

@login_required
def profile(request, id):
    if request.user.id == id:
        user = request.user
    else:
        user = get_object_or_404(User.objects.select_related('profile').prefetch_related('profile__preferences').only('first_name', 'last_name', 'profile__image', 'email', 'date_joined'), id=id)

    number_of_articles = Article.objects.filter(user=user).count()
    number_of_friends = ChatContact.objects.filter(Q(user_from=user, status='F')|Q(user_to=user, status='F')).count()

    if Contact.objects.filter(user_from = request.user, user_to = user).exists():
        is_user_follow = True
    else:
        is_user_follow = False

    try:
        chat_contact = ChatContact.objects.get(Q(user_from=request.user, user_to=user) | Q(user_from=user, user_to=request.user))
    except:
        contact_status = None
    else:
        contact_status = chat_contact.status

    context = {
        'user': user,
        'is_user_follow': is_user_follow,
        'contact_status': contact_status,
        'number_of_friends': number_of_friends,
        'number_of_articles': number_of_articles
    }
    return render(request, 'blog/profile.html', context)


@login_required
def user_edit(request):
    user = request.user
    if request.method=='POST':
        profile_form = ProfileCreateUpdateForm(instance=user.profile, data=request.POST, files=request.FILES)
        user_form = UserUpdateForm(instance=user, data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return render(request, 'blog/profile.html')

    else:
        profile_form = ProfileCreateUpdateForm(instance=user.profile)
        user_form = UserUpdateForm(instance=user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'blog/useredit.html', context)


@login_required
def profile_follow(request):
    if request.is_ajax():
        user = get_object_or_404(User, id = request.POST.get('id'))

        if not Contact.objects.filter(user_from = request.user, user_to = user).delete()[0]:
            Contact.objects.create(user_from = request.user, user_to = user)

        return JsonResponse({'status': 'ok'})


@login_required
def user_list(request):
    users = User.objects.only('first_name', 'last_name').all()
    return render(request, 'blog/users.html', {'users': users})

@login_required
def unsubscribe_from_newsletter(request):
    request.user.profile.is_subscribed_to_the_newsletter = False
    request.user.profile.save(update_fields=['is_subscribed_to_the_newsletter'])
    return redirect('blog:article_list')


@login_required
def add_to_friends(request):
    if request.is_ajax():
        user = get_object_or_404(User, id = request.POST.get('id'))
        action = request.POST.get('action')

        user_flag = request.user.id < user.id

        if user_flag:
            chat_contact = ChatContact.objects.filter(user_from=request.user, user_to=user)
        else:
            chat_contact = ChatContact.objects.filter(user_from=user, user_to=request.user)

        if action == 'add_to_friends':
            if not chat_contact:
                if user_flag:
                    chat_contact = ChatContact.objects.create(user_from=request.user, user_to=user, status='PF')

                else:
                    chat_contact = ChatContact.objects.create(user_from=user, user_to=request.user, status='PS')
                notify.send(request.user, recipient=user, action_object=request.user, verb='sent you a friend request.', description='friend_request')

        elif action == 'cancel_request':
            if chat_contact:
                chat_contact.delete()

        elif action == 'accept_request':
            if chat_contact:
                status_temp = chat_contact[0].status
                chat_contact.update(status='F')

                if status_temp == 'PF':
                    notify.send(chat_contact[0].user_to, recipient=chat_contact[0].user_from, action_object=chat_contact[0].user_to, verb='accepted your request.', description='friend_request')
                elif status_temp == 'PS':
                    notify.send(chat_contact[0].user_from, recipient=chat_contact[0].user_to, action_object=chat_contact[0].user_from, verb='accepted your request.', description='friend_request')

        elif action == 'remove_from_friends':
            if chat_contact:
                chat_contact.delete()

        else:
            return JsonResponse({'status': 'ko'})

        return JsonResponse({'status': 'ok'})

def user_articles_serializer(qs):
    object_list = []
    for i in qs:
        obj = {}
        obj['id'] = i.id
        obj['title'] = i.title
        obj['description'] = i.description
        obj['tags'] = []

        for tag in i.tags.all():
            obj['tags'].append(tag.name)
        object_list.append(obj)

    return object_list

@debugger_queries
@require_http_methods(["GET"])
@ajax_required
def get_user_articles(request):
    try:
        user_id = int(request.GET.get('user_id'))
        page = int(request.GET.get('page'))
    except:
        return HttpResponseBadRequest()
    else:
        packet_size = 6
        key = 'user_{}_articles_num_pages'.format(user_id)
        num_pages = cache.get(key)

        if not num_pages:
            num_pages = ceil(Article.objects.filter(user=user_id).count() / packet_size)
            cache.set(key, num_pages)

        qs = Article.objects.filter(user=user_id).only('id', 'title', 'description', 'tags__name').prefetch_related('tags')[(page-1)*packet_size:page*packet_size]
        object_list = user_articles_serializer(qs)

        data = {
            'num_pages': num_pages,
            'current_page': page,
            'articles': object_list
        }

        return JsonResponse({'data': data}, status='200')


def user_friend_serializer(user, chat_id=None):
    obj = {}
    obj['id'] = user.id
    obj['full_name'] = '{} {}'.format(user.first_name, user.last_name)
    obj['image'] = user.profile.get_image_url()
    if chat_id:
        obj['chat_id'] = chat_id
    return obj

@require_http_methods(["GET"])
@debugger_queries
@ajax_required
def get_user_friends(request):
    user_id = int(request.GET.get('user_id'))
    page = int(request.GET.get('page'))

    if request.user.id == user_id:
        user = request.user
        is_owner = True
    else:
        user = get_object_or_404(User.objects.only('id'), id=user_id)
        is_owner = False

    packet_size = 6
    key = 'user_{}_friends_num_pages'.format(user_id)
    num_pages = cache.get(key)

    if not num_pages:
        num_pages = ceil(ChatContact.objects.filter(Q(user_from=user, status='F') | Q(user_to=user, status='F')).count() / packet_size)
        cache.set(key, num_pages)

    qs = ChatContact.objects.select_related('user_to', 'user_from', 'user_to__profile', 'user_from__profile')\
        .only('id', 'user_from__id', 'user_from__first_name', 'user_from__last_name', 'user_from__profile__image', 'user_to__id', 'user_to__first_name', 'user_to__last_name', 'user_to__profile__image')\
        .filter(Q(user_from=user, status='F') | Q(user_to=user, status='F'))[(page-1)*packet_size:page*packet_size]

    request_user_friends_1 = request.user.friend_request_from.values_list('id', 'user_to').filter(status='F')
    request_user_friends_2 = request.user.friend_request_to.values_list('id', 'user_from').filter(status='F')

    request_user_friends = {}
    for u in request_user_friends_1:
        request_user_friends[u[1]] = u[0]

    for u in request_user_friends_2:
        request_user_friends[u[1]] = u[0]

    object_list = []
    for i in qs:
        if user.id == i.user_from.id:
            friend = i.user_to
        else:
            friend = i.user_from

        if not is_owner:
            chat_id = request_user_friends.get(friend.id, None)

        #     chat_id = None
        #     if request.user.id < friend.id:
        #         chat = ChatContact.objects.only('id').filter(user_from=request.user, user_to=friend, status='F')
        #     else:
        #         chat = ChatContact.objects.only('id').filter(user_from=friend, user_to=request.user, status='F')
        #
        #     if chat:
        #         chat_id = chat[0].id

        else:
            chat_id = i.id

        obj = user_friend_serializer(friend, chat_id)
        object_list.append(obj)

    data = {
        'num_pages': num_pages,
        'current_page': page,
        'friends': object_list,
        'is_owner': is_owner
    }

    return JsonResponse({'data': data}, status='200')
