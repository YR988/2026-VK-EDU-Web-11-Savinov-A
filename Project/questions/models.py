from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError


class DefaultModel(models.Model):
    class Meta:
        abstract=True

    is_active = models.BooleanField(default=True, verbose_name='Активен?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания',editable=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления',editable=False, null=True)



class User(AbstractUser):

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



class Tag(models.Model):
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    title = models.CharField(max_length=100, verbose_name='Названия тега')
    
    def __str__(self):
        return str(self.title)



class Question(DefaultModel):
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    title = models.CharField(max_length=200)
    detailed = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    raiting = models.IntegerField(default=0)
    answers_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')


    def __str__(self):
        return str(self.title)
    
    def update_answers_count(self):
        self.answers_count = self.answer_set.count()
        self.save()

    def update_rating(self):
        likes = self.questionlike_set.filter(is_negative=False).count()
        dislikes = self.questionlike_set.filter(is_negative=True).count()
        self.raiting = likes - dislikes
        self.save()

    def tags_display(self):
        return ", ".join([tag.title for tag in self.tags.all()])


class Answer(DefaultModel):
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    raiting = models.IntegerField(default=0)
    isCorrect = models.BooleanField(default=False)


    def __str__(self):
        return "Ответ на вопрос ID=" + str(self.question_id)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.question.update_answers_count()

    def delete(self, *args, **kwargs):
        question = self.question
        super().delete(*args, **kwargs)
        question.update_answers_count()

    def update_isCorrect(self):
        self.save()

    def update_rating(self):
        likes = self.anwserlike_set.filter(is_negative=False).count()
        dislikes = self.anwserlike_set.filter(is_negative=True).count()
        self.raiting = likes - dislikes
        self.save()
    

class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_negative = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ['question', 'author']

    def save(self, *args, **kwargs):
        if QuestionLike.objects.filter(question=self.question, author=self.author).exists():
            if not self.pk:
                raise ValidationError("Пользователь уже оценил этот вопрос")
        
        super().save(*args, **kwargs)
        self.question.update_rating()



class AnswerLike(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_negative = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ['answer', 'author']

    def save(self, *args, **kwargs):
        if AnswerLike.objects.filter(question=self.question, author=self.author).exists():
            if not self.pk:
                raise ValidationError("Пользователь уже оценил этот вопрос")
        
        super().save(*args, **kwargs)
        self.question.update_rating()