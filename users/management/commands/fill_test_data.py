from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Tutor, Student, Program, Lesson
from faker import Faker
import random
from datetime import datetime, timedelta
from django.utils import timezone

from schedule.models import TimeSlot
from users.models import StudentLesson

fake = Faker('ru_RU')
User = get_user_model()


class Command(BaseCommand):
    help = 'Fill database with test data'

    def handle(self, *args, **options):
        self.create_users()
        self.create_programs()
        self.create_timeslots()
        self.create_lessons()
        self.stdout.write(self.style.SUCCESS('Successfully filled database with test data'))

    def create_users(self):

        # Создаем 5 репетиторов
        for i in range(1, 6):
            user = User.objects.create_user(
                username=f'tutor{i}',
                email=f'tutor{i}@example.com',
                password='password123',
                user_type='tutor',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=f'+79{i}{fake.msisdn()[:9]}'
            )
            Tutor.objects.create(
                user=user,
                specialization=random.choice(['Математика', 'Физика', 'Программирование', 'Английский', 'История']),
                qualification=fake.text(),
                is_verified=True
            )

        # Создаем 10 студентов
        for i in range(1, 11):
            user = User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@example.com',
                password='password123',
                user_type='student',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=f'+79{i}{fake.msisdn()[:9]}'
            )
            Student.objects.create(
                user=user,
                education_level=random.choice(['elementary', 'middle', 'high', 'university'])
            )

    def create_programs(self):
        tutors = Tutor.objects.all()
        for tutor in tutors:
            for i in range(1, 4):  # 3 программы на каждого репетитора
                Program.objects.create(
                    tutor=tutor,
                    name=f"{tutor.specialization} {i} уровень",
                    description=fake.paragraph(),
                    price_per_hour=random.randint(500, 3000)
                )

    def create_timeslots(self):
        tutors = Tutor.objects.all()
        for tutor in tutors:
            for day in range(0, 14):  # Создаем слоты на 2 недели вперед
                date = timezone.now() + timedelta(days=day)
                # Создаем 3 слота в день
                for hour in [10, 14, 18]:  # Утро, день, вечер
                    start_time = timezone.make_aware(datetime.combine(date.date(), datetime.min.time())) + timedelta(
                        hours=hour)
                    end_time = start_time + timedelta(hours=2)
                    TimeSlot.objects.create(
                        tutor=tutor,
                        start_time=start_time,
                        end_time=end_time
                    )

    def create_lessons(self):
        programs = Program.objects.all()
        students = Student.objects.all()
        tutors = Tutor.objects.all()

        for tutor in tutors:
            timeslots = TimeSlot.objects.filter(tutor=tutor, start_time__gte=timezone.now() - timedelta(days=7))
            for i, slot in enumerate(timeslots):
                if i % 3 == 0:  # Каждое третье занятие отменено
                    status = 'canceled'
                elif i % 5 == 0:  # Каждое пятое - в будущем
                    status = 'planned'
                else:
                    status = 'completed'

                lesson = Lesson.objects.create(
                    tutor=tutor,
                    program=random.choice(programs),
                    datetime=slot.start_time,
                    duration=random.choice([30, 60, 90]),
                    topic=fake.sentence(),
                    status=status
                )

                # Добавляем 1-3 случайных студентов на занятие
                lesson.students.set(random.sample(list(students), k=random.randint(1, 3)))

                # Для завершенных занятий добавляем оценки
                if status == 'completed':
                    for student in lesson.students.all():
                        StudentLesson.objects.create(
                            student=student,
                            lesson=lesson,
                            grade=random.randint(1, 5),
                            feedback=fake.paragraph()
                        )