from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from questions.models import User, Question, Answer, Tag, AnswerLike, QuestionLike

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display  = ('id', 'username', 'email', 'avatar')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('avatar',)}),
    )




@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author','raiting', 'is_active', 'created_at', 'updated_at')
    list_filter = ('tags', 'is_active', 'created_at')
    filter_horizontal = ('tags',) 

    class AnswerInLine(admin.TabularInline):
        model = Answer
        extra = 0

    inlines = (AnswerInLine,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_active','isCorrect', 'created_at', 'updated_at')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_negative', 'get_question_author')
    list_filter = ('is_negative',)
    search_fields = ('question__title', 'author__username')
    
    def get_question_author(self, obj):
        return obj.question.author.username
    get_question_author.short_description = 'Автор вопроса'

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'author', 'is_negative', 'get_answer_author')
    list_filter = ('is_negative',)
    search_fields = ('answer__answer_text', 'author__username')
    
    def get_answer_author(self, obj):
        return obj.answer.author.username
    get_answer_author.short_description = 'Автор ответа'