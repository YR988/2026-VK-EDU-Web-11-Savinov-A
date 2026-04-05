from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from questions.models import Question, Answer


def settings(request, *args, **kwarags):
    return render(request, 'settings.html')

def login(request, *args, **kwarags):
    return render(request, 'login.html')

def signup(request, *args, **kwarags):
    return render(request, 'signup.html')

def ask(request, *args, **kwarags):
    return render(request, 'ask.html')

def question(request, question_id):
    question_obj = get_object_or_404(Question.objects.prefetch_related('tags'), id=question_id, is_active=True)
    answers = Answer.objects.filter(question=question_obj, is_active=True).select_related('author')

    paginated_questions = paginate(answers, request, per_page=3)

    context = {
        'question': question_obj,  
        'answers': paginated_questions,        
    }

    return render(request, 'question.html', context)

def paginate(objects_list, request, per_page=3):
    current_page = Paginator(objects_list, per_page)
    page_number = request.GET.get('page',1)
    page_obj = current_page.get_page(page_number)
    return page_obj

def index(request):
    questions = Question.objects.filter(is_active=True).prefetch_related('tags')

    author_name = request.GET.get('author')
    if author_name:
        questions = questions.filter(author__username=author_name)

    tag_name = request.GET.get('tag')
    if tag_name:
        questions = questions.filter(tags__title=tag_name)

    filter_name = request.GET.get('filter')
    if filter_name=='hot_question':
        questions = questions.order_by('-raiting')

    paginated_questions = paginate(questions, request, per_page=3)
    context = {
        'questions': paginated_questions
    }

    return render(request, 'index.html', context)

