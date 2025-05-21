from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.urls import reverse


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Ученик'),
        ('tutor', 'Репетитор'),
        ('admin', 'Администратор'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Максимум 15 цифр."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    middle_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    EDUCATION_LEVEL_CHOICES = [
        ('elementary', 'Начальная школа'),
        ('middle', 'Средняя школа'),
        ('high', 'Старшая школа'),
        ('university', 'Университет'),
    ]
    education_level = models.CharField(max_length=10, choices=EDUCATION_LEVEL_CHOICES)


class Tutor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    qualification = models.TextField()
    specialization = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_verified = models.BooleanField(default=False)


class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    documents = models.FileField(upload_to='media/verification_docs/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Запрос верификации'
        verbose_name_plural = 'Запросы верификации'

    def __str__(self):
        return f"Запрос верификации {self.tutor.user.get_full_name()}"
class Program(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['tutor', 'name']

    def __str__(self):
        return f"{self.name} ({self.tutor.user.get_full_name()})"

    def get_absolute_url(self):
        return reverse('program_detail', kwargs={'pk': self.pk})

    def get_average_rating(self):
        avg = self.lessons.aggregate(Avg('studentlesson__grade'))['studentlesson__grade__avg']
        return round(avg, 1) if avg else None


class Lesson(models.Model):
    LESSON_STATUS = [
        ('planned', 'Запланировано'),
        ('completed', 'Проведено'),
        ('canceled', 'Отменено'),
    ]
    datetime = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Продолжительность в минутах")
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=LESSON_STATUS, default='planned')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    students = models.ManyToManyField(Student, through='StudentLesson')
    tutor_notes = models.TextField(blank=True, null=True, verbose_name="Заметки репетитора")

    @property
    def cost(self):
        if self.program:
            return (self.duration / 60) * self.program.price_per_hour
        return 0

    def save(self, *args, **kwargs):
        # При отметке как "Проведено" обновляем рейтинг
        if self.status == 'completed' and self.pk:
            original = Lesson.objects.get(pk=self.pk)
            if original.status != 'completed':
                self.update_tutor_rating()
        super().save(*args, **kwargs)

        if self.pk and self.status == 'canceled':
            original = Lesson.objects.get(pk=self.pk)
            if original.status != 'canceled':
                pass
        super().save(*args, **kwargs)

    def update_tutor_rating(self):
        """Обновляет рейтинг репетитора на основе оценок"""
        completed_lessons = Lesson.objects.filter(
            tutor=self.tutor,
            status='completed',
            studentlesson__grade__isnull=False
        )
        avg_rating = completed_lessons.aggregate(
            avg_grade=Avg('studentlesson__grade')
        )['avg_grade'] or 0
        self.tutor.rating = round(avg_rating, 1)
        self.tutor.save()

class StudentLesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    feedback = models.TextField(blank=True, null=True, verbose_name="Отзыв")


class Schedule(models.Model):
    DAY_OF_WEEK_CHOICES = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK_CHOICES)
    is_recurring = models.BooleanField(default=True)


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Неудачный'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Перевод'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)