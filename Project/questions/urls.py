from django.urls import path

from . import views
from questions.views import index, login, settings, signup, question, ask



urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('settings/', settings, name='settings'),
    path('signup/', signup, name='signup' ),
    path('question/', question, name='question'),
    path('ask/', ask, name='ask'),
    path('question/<int:question_id>/', views.question, name='question_detail'),
    
]