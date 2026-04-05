from django.db.models import Count
from questions.models import Tag, User

def popular_tags(request):
    tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    return {'tags': tags}

def popular_profiles(request):
    users = User.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    return {'users': users}