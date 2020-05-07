from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import QuestionChoicesFormSet, QuestionForm, QuizForm
from .models import Quiz, Question, QuestionChoices, QuestionAnswer
from django.forms.models import modelform_factory
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseNotFound
from blog.models import Category
from random import shuffle, random
from django.contrib.sessions.models import Session
from accounts.models import Profile
from django.core.cache import cache

import time
from Blog.decorators import debugger_queries
from django.db.models import Prefetch

from django.db.models import prefetch_related_objects

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_protect
from django.db.models import Prefetch

from django.http import HttpResponse


class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/list.html'
    slug = None
    paginate_by = 4

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.kwargs.get('slug'):
            qs = qs.filter(category__slug=self.kwargs['slug'])
            self.slug = self.kwargs['slug']
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        if self.slug:
            context['category'] = get_object_or_404(Category, slug=self.slug)
        return context

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quiz/detail.html'

@method_decorator(login_required, name='dispatch')
class QuizCreateUpdateView(TemplateResponseMixin, View):
    model = Quiz
    object = None
    template_name = 'quiz/manage/quiz.html'
    form_class = QuizForm

    def dispatch(self, request, id=None):
        if id:
            self.object = get_object_or_404(self.model, id=id)
            if self.object.user_id != request.user.id:
                return HttpResponse(status=403)

        return super(QuizCreateUpdateView, self).dispatch(request, id)

    # def get_form(self, model, *args, **kwargs):
    #     Form = modelform_factory(model, exclude=['user', 'created', 'updated'])
    #     return Form(*args, **kwargs)

    def get(self, request, id=None):
        form = QuizForm(instance=self.object)
        return render(request, self.template_name, {'form': form, 'object': self.object})

    def post(self, request, id=None):
        form = QuizForm(instance=self.object, data=request.POST)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.save()
            return redirect(reverse('quiz_detail', args=[self.object.id]))
        return render(request, self.template_name, {'form': form})


class QuizQuestionCreateUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    quiz = None
    object = None
    template_name = 'quiz/manage/questions.html'

    def dispatch(self, request, quiz_id, id=None):
        self.quiz = get_object_or_404(Quiz, id=quiz_id)
        if self.quiz.user_id != request.user.id:
            return HttpResponse(status=403)
        if id:
            self.object = get_object_or_404(Question, id=id, quiz=self.quiz)

        return super(QuizQuestionCreateUpdateView, self).dispatch(request, quiz_id, id)

    def get(self, request, quiz_id, id=None):
        question_choices_formset = QuestionChoicesFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(object=self.object, question_choices_formset=question_choices_formset))

    def post(self, request, quiz_id, id=None):
        form = self.get_form(self.form_class)
        question_choices_formset = QuestionChoicesFormSet(instance=self.object, data=self.request.POST)

        if form.is_valid():
            if question_choices_formset.is_valid():
                return self.form_valid(form, question_choices_formset)
            else:
                return self.form_valid(form, None)
        else:
            return self.form_invalid(form, question_choices_formset)

        return self.render_to_response(self.get_context_data(object=self.object, question_choices_formset=question_choices_formset))

    def form_valid(self, form, question_choices_formset):
        self.object = form.save(commit=False)
        self.object.quiz = self.quiz
        self.object.save()

        if question_choices_formset:
            question_choices_formset.instance = self.object
            question_choices_formset.save()

        question_choices_formset = QuestionChoicesFormSet(instance=self.object)

        return self.render_to_response(self.get_context_data(object=self.object, question_choices_formset=question_choices_formset))

    def form_invalid(self, form, question_choices_formset):
        return self.render_to_response(self.get_context_data(question_choices_formset=question_choices_formset))


@debugger_queries
@login_required
def take_quiz(request, id):
    key = 'quiz_{}'.format(id)
    quiz = cache.get(key)

    if not quiz:
        quiz = Quiz.objects.prefetch_related('questions', 'questions__choices').get(id=id)
        cache.set(key, quiz)

    if request.user.profile in quiz.profiles.all():
        is_user_pass = True
    else:
        is_user_pass = False

    context = {
        'quiz': quiz,
        'is_user_pass': is_user_pass,
    }

    return render(request, 'quiz/take.html', context)


@debugger_queries
@require_http_methods(["POST"])
def recive_user_answer(request):
    if request.is_ajax():
        key = 'quiz_{}'.format(request.POST.get('quiz_id'))
        quiz = cache.get(key)

        if not quiz:
            quiz = Quiz.objects.prefetch_related('questions', 'questions__choices').get(id=id)
            cache.set(key, quiz)

        question = [question for question in quiz.questions.all() if question.id == int(request.POST.get('question_id'))]
        if not question:
            return HttpResponseNotFound('Question not found.')
        question  = question[0]

        # try:
        #     question = quiz.questions.get(id=request.POST.get('question_id'))
        # except Question.DoesNotExist:
        #     return HttpResponseNotFound('Question not found.')

        right_choice = [choice for choice in question.choices.all() if choice.is_right_choice]
        right_choice = right_choice[0]
        is_right = False
        if right_choice.id == int(request.POST.get('id')):
            is_right = True

        last_question_order = quiz.questions.values('order').last()
        if question.order == last_question_order['order']:
            is_last_question = True
        else:
            is_last_question = False

        question_answer = QuestionAnswer.objects.filter(user=request.user, question=question)
        if not question_answer:
            QuestionAnswer.objects.create(user=request.user, question=question, is_right=is_right)
        else:
            if question_answer[0].is_right != is_right:
                question_answer.update(is_right=is_right)

        #QuestionAnswer.objects.update_or_create(user=request.user, question=question, defaults={'is_right': is_right}) # 5 queries
        return JsonResponse({'is_right': is_right, 'right_choice_id': right_choice.id, 'is_last_question': is_last_question})

@debugger_queries
@require_http_methods(["GET"])
def get_next_question(request):
    if request.is_ajax():
        key = 'quiz_{}'.format(request.GET.get('quiz_id'))
        quiz = cache.get(key)

        if not quiz:
            quiz = Quiz.objects.prefetch_related('questions', 'questions__choices').get(id=request.GET.get('quiz_id'))
            cache.set(key, quiz)

        question = [question for question in quiz.questions.all() if question.order == int(request.GET.get('question_order'))]
        try:
            question = question[0]
        except:
            print(question)

        if not question:
            return JsonResponse({'is_quiz_end': True})

        # try:
        #     question = quiz.questions.get(order=request.GET.get('question_order'))
        # except Question.DoesNotExist:
        #     return JsonResponse({'is_quiz_end': True})

        question_order = question.order + 1
        choices = list(question.choices.values('id', 'question_id', 'choice'))
        shuffle(choices)
        choices_count = len(choices)
        context = {
            'question': question.question,
            'choices_count': choices_count,
            'question_order': question_order,
        }

        for i in range(choices_count):
            context['choice'+str(i)] = choices[i]

        return JsonResponse(context)

@debugger_queries
@require_http_methods(["POST"])
def add_quiz_to_profile(request):
    if request.is_ajax():
        key = 'quiz_{}'.format(request.POST.get('quiz_id'))
        quiz = cache.get(key)

        if not quiz:
            quiz = Quiz.objects.get(id=request.POST.get('quiz_id'))

        session_key = request.POST.get('session_key')
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        profile = Profile.objects.get(user__id=uid)
        profile.passed_quizzes.add(quiz)

        return JsonResponse({'status': 'ok'})

@login_required
def test_new_quiz(request, id):
    quiz = Quiz.objects.prefetch_related('questions', 'questions__choices').get(id=id)


    if request.user.is_authenticated and request.user.profile in quiz.profiles.all():
        is_user_pass = True
    else:
        is_user_pass = False

    context = {
        'quiz': quiz,
        'is_user_pass': is_user_pass,
    }

    return render(request, 'quiz/quizstart.html', context)

@csrf_protect
@require_http_methods(["POST"])
@login_required
def check_and_display_user_answers(request):
    if request.is_ajax():
        quiz_id = request.POST.get('quiz_id')
        user_choices = request.POST.getlist('user_choices')

        questions = Question.objects.defer('question', 'order').filter(quiz__id=quiz_id).prefetch_related(Prefetch('choices', queryset=QuestionChoices.objects.defer('choice')))

        answers_to_create = []
        answers_to_update = []

        # quiz step, see in quizstart.html
        step = 0
        answers_bit_vector = []
        for question in questions:
            # ???query optimization, when i using filter() or get() the number of queries is incresing.
            right_choice = [choice for choice in question.choices.all() if choice.is_right_choice]
            right_choice = right_choice[0]

            if right_choice.id == int(user_choices[step]):
                answers_bit_vector.append(1)
            else:
                answers_bit_vector.append(0)

            question_answer = QuestionAnswer.objects.filter(user=request.user, question=question)
            if not question_answer:
                answers_to_create.append(QuestionAnswer(user=request.user, question=question, is_right=answers_bit_vector[step]))
            else:
                if question_answer[0].is_right != answers_bit_vector[step]:
                    question_answer[0].is_right = answers_bit_vector[step]
                    answers_to_update.append(question_answer[0])
            step += 1

        QuestionAnswer.objects.bulk_create(answers_to_create)
        QuestionAnswer.objects.bulk_update(answers_to_update, ['is_right'])

        is_user_pass_quiz = all(answers_bit_vector)
        if is_user_pass_quiz:
            request.user.profile.passed_quizzes.add(quiz_id)

        data = {
            'status_code': '201',
            'success_url': '/quizzes/results/',
            'answers_bit_vector': answers_bit_vector,
            'is_user_pass_quiz': is_user_pass_quiz,
        }

        return JsonResponse(data, status='201')

def quiz_create_update(request):
    return render(request, 'quiz/edit.html', {})
