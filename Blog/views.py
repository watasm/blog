from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm, ArticleUpdateForm, CategoryForm, CommentForm, EmailArticleForm, SearchForm
from django.contrib.auth.models import User
from .models import Article, Category, Comment, Bookmark
from django.template.defaultfilters import slugify
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.views.generic.edit import UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from urllib.parse import quote_plus
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.auth.mixins import LoginRequiredMixin
from notifications.signals import notify
from django.utils.html import mark_safe
from django.views.decorators.http import require_http_methods
from notifications.models import Notification
from django.contrib.sessions.models import Session

from django.views import View
from django.db.models import Count
import json
from django.views.decorators.csrf import csrf_protect
from math import ceil

def article_list(request, slug=None):
    packet_size = 4
    num_pages = ceil(Article.objects.count() / packet_size)
    categories = Category.objects.all().annotate(articles_count=Count('article'))

    try:
        page = int(request.GET.get('page'))
    except:
        page = 1

    if page > num_pages:
        page = num_pages

    articles = Article.objects.defer('text', 'user__username', 'user__password', 'user__email').select_related('user').prefetch_related('tags')\
                .all()[(page-1)*packet_size:page*packet_size]
    popular_articles = list(Article.objects.annotate(total_likes=Count('like'), total_comments=Count('comments'))\
                        .order_by('-total_likes', '-total_comments')[:4])

    if slug:
        category = get_object_or_404(Category, slug=slug)
        object_list = object_list.filter(category=category)

    # create custom paginator
    # paginator = Paginator(object_list, 4)
    # page = request.GET.get('page')
    # try:
    #     articles = paginator.page(page)
    # except PageNotAnInteger:
    #     articles = paginator.page(1)
    # except EmptyPage:
    #     articles = paginator.page(paginator.num_pages)

    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'text', 'category__name', 'user__username')
            search_query = SearchQuery(query)
            results = Article.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank').distinct('rank')

            return render(request,'blog/search.html', {'form': form, 'query': query, 'results': results})
    page_range = range(1, num_pages+1)
    return render(request, 'blog/index.html', {'articles':articles, 'categories': categories, 'form': form, 'popular_articles': popular_articles, 'num_pages': num_pages, 'current_page': page, 'page_range': page_range})


@receiver(m2m_changed, sender = Article.category.through)
def update_category_not_send(sender, instance, **kwargs):
    if instance.category.all():
        categories = instance.category.all()
        for cat in categories:
            Category.objects.filter(id=cat.id).update(not_sended=True)


def article_post_save(sender, instance, created, **kwargs):
    notify.send(instance.user, recipient=instance.user.followers.all(), action_object=instance, verb='add new article.')

post_save.connect(article_post_save, sender=Article)

@login_required
def add_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.user = request.user
            new_article.save()
            form.save_m2m()

            return redirect('blog:article_list')
    else:
        form = ArticleForm()

    return render(request, 'blog/manage/article.html', {'form': form})

def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    similar_articles = article.tags.similar_objects()[:5]
    comments = article.comments.all().annotate(likes_count=Count('comment_likes')).select_related('user', 'user__profile')\
    .defer('user__email', 'user__username', 'user__password', 'user__profile__preferences', 'user__profile__passed_quizzes', 'user__profile__is_subscribed_to_the_newsletter')\
    .order_by('-post_date')

    share_string_desc = quote_plus(article.description)

    context = {
        'article':article,
        'is_article_liked': article.like.filter(id = request.user.id).exists(),
        'total_likes': article.total_likes(),
        'comment_form': CommentForm(),
        'share_string_desc': share_string_desc,
        'similar_articles': similar_articles,
        'comments': comments,
        'comments_count': len(comments),
        'is_bookmarked': Bookmark.objects.filter(user__id=request.user.id, article=article).exists()
    }
    return render(request, 'blog/article_detail.html', context)

@login_required
def add_category(request):
    category = CategoryForm()

    if request.method == 'POST':
        category = CategoryForm(request.POST)

        if category.is_valid():
            new_category = category.save(commit=False)
            new_category.slug = slugify(new_category.name)
            new_category.save()
            return redirect('blog:article_list')

    return render(request, 'blog/add_category.html', {'category_form':category})

@csrf_protect
@require_http_methods(["POST"])
@login_required
def like_article(request):
    if request.is_ajax():
        article = get_object_or_404(Article, id = request.POST.get('id'))
        status = None

        if not article.user_id == request.user.id:
            if article.like.filter(id=request.user.id).exists():
                status = 'unliked'
                article.like.remove(request.user)
            else:
                article.like.add(request.user)
                status = 'liked'

        return JsonResponse({'status': status})

@csrf_protect
@require_http_methods(["POST"])
@login_required
def like_comment(request):
    if request.is_ajax():
        comment = get_object_or_404(Comment, id=request.POST.get('id'))
        status = None

        if not comment.user_id == request.user.id:
            if comment.comment_likes.filter(id=request.user.id).exists():
                comment.comment_likes.remove(request.user)
                status = 'unliked'
            else:
                comment.comment_likes.add(request.user)
                status = 'liked'

        return JsonResponse({'status': status})


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class=ArticleUpdateForm
    template_name = 'blog/article_edit.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_authenticated:
            if obj.user != self.request.user and not request.user.is_superuser:
                raise PermissionDenied
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('account_login')


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'blog/article_delete.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_authenticated:
            if obj.user != self.request.user and not request.user.is_superuser:
                raise PermissionDenied
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('account_login')
    success_url = reverse_lazy('blog:article_list')

@login_required
def article_share(request, pk):
    article = get_object_or_404(Article, id=pk)
    sent = False
    if request.method == 'POST':
        email_form = EmailArticleForm(request.POST)
        if email_form.is_valid():
            cd = email_form.cleaned_data
            article_url = request.build_absolute_uri(article.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], article.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(article.title, article_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        email_form = EmailArticleForm()

    return render(request, 'blog/share.html', {'article':article, 'email_form': email_form, 'sent': sent})

def article_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'text', 'category__name', 'user__username')
            search_query = SearchQuery(query)
            results = Article.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank').distinct('rank')

    return render(request,'blog/search.html', {'form': form, 'query': query, 'results': results})


@require_http_methods(["POST"])
@login_required
def mark_notification_as_read(request):
    if request.is_ajax():
        try:
            Notification.objects.get(id=request.POST.get('id')).mark_as_read()
        except:
            return JsonResponse({'marked': False})
        else:
            return JsonResponse({'marked': True})


@require_http_methods(["POST"])
@login_required
def mark_all_notifications_as_read(request):
    if request.is_ajax():
        session_key = request.POST.get('session_key')
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        user = User.objects.get(id=uid)
        qs = Notification.objects.filter(recipient=user)
        qs.mark_all_as_read()
        return JsonResponse({'status': 'ok'})

from .documents import ArticleDocument

class ElasticSearchView(View):
    template_name = 'blog/search_result.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        query = " ".join(query.split())
        search_results = None
        if query:
            try:
                values = query.split()
            except:
                pass
            else:
                title_clauses = []
                text_clauses = []
                for value in values:
                    title_clauses.append({'span_multi':{'match':{'fuzzy':{'title':{"fuzziness": "AUTO", "value": value}}}}})
                    text_clauses.append({'span_multi':{'match':{'fuzzy':{'text':{"fuzziness": "AUTO", "value": value}}}}})

                try:
                    search_results = ArticleDocument.search().query('bool', should=[{'span_near':{'clauses':title_clauses, 'in_order':'false', 'slop':'1'}}, {'span_near':{'clauses':text_clauses, 'in_order':'false', 'slop':'1'}}])
                except:
                    search_results = 'Illegal characters.'
                else:
                    search_results = search_results.highlight_options(pre_tags='<b>', post_tags='</b>')
                    search_results = search_results.highlight('text')
                    
        return render(request, self.template_name, {'search_results': search_results})

@csrf_protect
@require_http_methods(["POST"])
@login_required
def add_bookmark(request):
    if request.is_ajax():
        try:
            Bookmark.objects.get(user=request.user, article_id=request.POST.get('id')).delete()
        except Bookmark.DoesNotExist:
            Bookmark.objects.create(user=request.user, article_id=request.POST.get('id'))
            status = 'added'
        else:
            status = 'removed'

        return JsonResponse({'status': status})
