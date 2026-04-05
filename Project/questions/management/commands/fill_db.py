from asyncio import taskgroups
import random
import typing as t
from django.core.management.base import BaseCommand
from django.db import connection
from questions.models import Question, User, Tag, Answer

class Command(BaseCommand):
    help = 'Генерация сущностей по модели Вопроса'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')


    def get_exist_user(sefl) -> t.Optional[User]:
        return User.objects.filter(is_superuser=True).first()

    def handle(self, *args, **options):
        ratio = options['ratio']

       
        # Создание пользователей
        users_to_create = []
        for i in range(ratio):
            user = User(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password={i},
                first_name=f'User{i}',
                last_name=f'Testov',
                is_active=True
            )
            users_to_create.append(user)

        User.objects.bulk_create(users_to_create, batch_size=100)
        self.stdout.write(self.style.SUCCESS(f'Создано {User.objects.count()} пользователей'))
        users = list(User.objects.all())


        # Создание тегов
        tags_to_create = []
        for i in range(ratio):
            tag = Tag(
                title=f'tag_{i}'
            )
            tags_to_create.append(tag)
        
        Tag.objects.bulk_create(tags_to_create, batch_size=100)
        tags = list(Tag.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Создано {len(tags)} тегов'))

        # Создание вопросов
        count_exist_questions = Question.objects.count()
        questions_to_create = []
        for n in range(ratio * 10):
            questions_to_create.append(Question(
                title=f"Question {count_exist_questions + n + 1}",
                detailed=FAKE_QUESTION_DETAILED,
                author=random.choice(users)
            ))

        Question.objects.bulk_create(questions_to_create, batch_size=100)
        questions = list(Question.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Создано {len(questions)} вопросов'))



        # Добавление тегов к вопросам
        tag_groups = [tags[i:i+3] for i in range(0, len(tags), 3)]

        # Создаем связи через промежуточную таблицу
        through_model = Question.tags.through
        question_tag_relations = []

        for i, question in enumerate(questions):
            group_index = i % len(tag_groups)
            for tag in tag_groups[group_index]:
                question_tag_relations.append(
                    through_model(question_id=question.id, tag_id=tag.id)
                )
            
            # Пакетно сохраняем каждые 1000 связей
            if len(question_tag_relations) >= 1000:
                through_model.objects.bulk_create(question_tag_relations, batch_size=1000)
                question_tag_relations = []

        # Сохраняем оставшиеся связи
        if question_tag_relations:
            through_model.objects.bulk_create(question_tag_relations, batch_size=1000)
        self.stdout.write(self.style.SUCCESS('Теги добавлены к вопросам'))


        # Создание ответов
        answers_to_create = []
        for i in range(ratio * 100):
            question_index = i % len(questions)
            user_index = i % len(users)
            answer = Answer(
                question=questions[question_index],
                answer_text=FAKE_ANSWER_DETAILED,
                author=users[user_index],
                raiting=0,
                isCorrect=(i % 3 == 0)
            )
            answers_to_create.append(answer)
        
        Answer.objects.bulk_create(answers_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Создано {Answer.objects.count()} ответов'))


        # Обновление кол-во ответов на вопрос
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE questions_question 
            SET answers_count = (
                SELECT COUNT(*) 
                FROM questions_answer 
                WHERE questions_answer.question_id = questions_question.id
            )
            """)
        self.stdout.write(self.style.SUCCESS('Счетчики ответов обновлены'))


        self.stdout.write(self.style.SUCCESS(f'- Пользователи: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Вопросы: {Question.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Ответы: {Answer.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Теги: {Tag.objects.count()}'))

FAKE_QUESTION_DETAILED = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum 
dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
mollit anim id est laborum."""

FAKE_ANSWER_DETAILED = """Itaque earum rerum hic tenetur a sapiente delectus, qui blanditiis praesentium voluptatum deleniti 
atque corrupti, quos dolores et quas molestias excepturi sint, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.
Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, sunt in culpa qui officia deserunt mollit anim id est laborum!"""