import logging
from venv import logger

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from users.models import Tutor, Schedule, Payment, Lesson, Program, StudentLesson
from .forms import TutorSearchForm
from schedule.models import TimeSlot
from users.forms import CompleteLessonForm, GradeLessonForm


def tutor_search(request):
    form = TutorSearchForm(request.GET or None)
    tutors = Tutor.objects.filter(is_verified=True)

    if form.is_valid():
        if form.cleaned_data['specialization']:
            tutors = tutors.filter(specialization__icontains=form.cleaned_data['specialization'])
        if form.cleaned_data['min_rating']:
            tutors = tutors.filter(rating__gte=form.cleaned_data['min_rating'])
        if form.cleaned_data['is_verified']:
            tutors = tutors.filter(is_verified=True)

    return render(request, 'bookings/tutor_search.html', {
        'form': form,
        'tutors': tutors,
    })


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'bookings/lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        context['is_tutor'] = hasattr(self.request.user, 'tutor')
        context['now'] = timezone.now()
        if context['is_tutor']:
            context['complete_form'] = CompleteLessonForm(instance=lesson)
        else:
            student_lesson, created = StudentLesson.objects.get_or_create(
                student=self.request.user.student,
                lesson=lesson
            )
            context['grade_form'] = GradeLessonForm(instance=student_lesson)

        return context


from django.views.generic.edit import UpdateView


class CompleteLessonView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = CompleteLessonForm
    template_name = 'bookings/complete_lesson.html'

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user.tutor)

    def form_valid(self, form):
        form.instance.status = 'completed'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('lesson_detail', kwargs={'pk': self.object.pk})


class GradeLessonView(LoginRequiredMixin, UpdateView):
    model = StudentLesson
    form_class = GradeLessonForm
    template_name = 'bookings/grade_lesson.html'

    def get_queryset(self):
        return super().get_queryset().filter(student=self.request.user.student)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.lesson.update_tutor_rating()
        return response

    def get_success_url(self):
        return reverse('lesson_detail', kwargs={'pk': self.object.lesson.pk})


class CancelLessonView(LoginRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'bookings/lesson_confirm_cancel.html'
    success_url = reverse_lazy('my_lessons')

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'tutor'):
            return qs.filter(tutor=self.request.user.tutor)
        elif hasattr(self.request.user, 'student'):
            return qs.filter(students=self.request.user.student)
        return qs.none()

    def form_valid(self, form):
        lesson = self.get_object()
        lesson.status = 'canceled'
        lesson.save()

        messages.success(self.request, "Занятие успешно отменено. Слот освобожден.")
        return redirect(self.get_success_url())


class MyLessonsView(LoginRequiredMixin, ListView):
    template_name = 'bookings/my_lessons.html'
    context_object_name = 'lessons'
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()

        if hasattr(self.request.user, 'tutor'):
            # Для репетитора - все его занятия
            return Lesson.objects.filter(
                tutor=self.request.user.tutor
            ).select_related('tutor__user').prefetch_related('students__user').order_by('-datetime')

        elif hasattr(self.request.user, 'student'):
            # Для ученика - только его занятия
            return Lesson.objects.filter(
                students=self.request.user.student
            ).select_related('tutor__user').order_by('-datetime')

        return Lesson.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['upcoming_lessons'] = self.get_queryset().filter(datetime__gte=now)
        context['past_lessons'] = self.get_queryset().filter(datetime__lt=now)

        if hasattr(self.request.user, 'tutor'):
            context['is_tutor'] = True
        else:
            context['is_tutor'] = False

        return context


from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib import messages


class TutorDetailView(DetailView):
    model = Tutor
    template_name = 'bookings/tutor_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Tutor, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutor = self.object

        # Получаем слоты на 2 недели вперед
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=14)

        # Получаем все доступные слоты репетитора
        time_slots = TimeSlot.objects.filter(
            tutor=tutor,
            end_time__gte=timezone.now(),
            start_time__lte=timezone.make_aware(
                timezone.datetime.combine(end_date, timezone.datetime.max.time())
            )
        ).order_by('start_time')

        # Получаем занятые слоты (существующие уроки)
        booked_lessons = Lesson.objects.filter(
            tutor=tutor,
            datetime__gte=timezone.now(),
            status__in=['planned', 'completed'],
            datetime__lte=timezone.make_aware(
                timezone.datetime.combine(end_date, timezone.datetime.max.time())
            )
        )

        # Получаем программы репетитора
        show_all = self.request.GET.get('show_all_programs') == '1'
        programs = tutor.programs.all().order_by('-created_at')[:10]
        has_programs = programs.exists()

        if not show_all:
            programs = programs[:10]  # Ограничиваем 10 программами
        days_dict = {}

        for slot in time_slots:
            current = max(slot.start_time, timezone.now())
            while current + timedelta(minutes=30) <= slot.end_time:
                slot_end = current + timedelta(minutes=30)
                day = current.date()

                if day not in days_dict:
                    days_dict[day] = []

                # Проверяем, не занято ли это время
                is_available = not any(
                    l.datetime <= current < l.datetime + timedelta(minutes=l.duration)
                    for l in booked_lessons
                )

                days_dict[day].append({
                    'start': current,
                    'end': slot_end,
                    'is_available': is_available,
                    'was_canceled': Lesson.objects.filter(
                        tutor=tutor,
                        datetime__gte=current,
                        datetime__lt=slot_end,
                        status='canceled'
                    ).exists()
                })

                current = slot_end

        # Формируем список дней со слотами
        available_days = []
        for day, slots in days_dict.items():
            if slots:
                available_days.append({
                    'date': day,
                    'slots': sorted(slots, key=lambda x: x['start'])
                })

        context.update({
            'available_days': sorted(available_days, key=lambda x: x['date']),
            'programs': programs,
            'has_programs': programs.exists(),
            'programs_count': tutor.programs.count(),
            'now': timezone.now(),
            'show_all_programs': show_all
        })
        return context

    logger = logging.getLogger(__name__)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tutor = self.object
        student = request.user.student

        try:
            with transaction.atomic():  # Используем транзакцию для целостности данных
                # Получаем данные из формы
                start_time_str = request.POST.get('start_time')
                duration = int(request.POST.get('duration', 60))
                topic = request.POST.get('topic', '').strip()
                program_id = request.POST.get('program')

                # Базовые проверки
                if not start_time_str:
                    raise ValueError("Не указано время начала занятия")
                if not topic:
                    raise ValueError("Не указана тема занятия")
                if not program_id:
                    raise ValueError("Не выбрана программа обучения")

                # Проверяем программу
                program = get_object_or_404(Program, id=program_id, tutor=tutor)

                # Преобразуем время с учетом часового пояса
                naive_start_time = timezone.datetime.fromisoformat(start_time_str)
                start_time = timezone.make_aware(naive_start_time)
                end_time = start_time + timedelta(minutes=duration)

                # Проверка на занятость времени (исключаем отмененные занятия)
                overlapping_lessons = Lesson.objects.filter(
                    tutor=tutor,
                    datetime__lt=end_time,
                    datetime__gte=start_time
                ).exclude(status='canceled')

                if overlapping_lessons.exists():
                    raise ValueError("Это время уже занято другим занятием")

                # Проверяем, что время попадает в доступный слот
                slot_exists = TimeSlot.objects.filter(
                    tutor=tutor,
                    start_time__lte=start_time,
                    end_time__gte=end_time
                ).exists()

                if not slot_exists:
                    # Проверяем, возможно это ранее отмененное занятие
                    was_canceled = Lesson.objects.filter(
                        tutor=tutor,
                        datetime__gte=start_time,
                        datetime__lt=end_time,
                        status='canceled'
                    ).exists()

                    if not was_canceled:
                        raise ValueError("Выбранное время недоступно для записи")

                # Создаем новое занятие
                lesson = Lesson(
                    datetime=start_time,
                    duration=duration,
                    topic=topic,
                    tutor=tutor,
                    program=program,
                    status='planned'
                )
                lesson.save()  # Сохраняем сначала без students
                lesson.students.add(student)  # Затем добавляем студента

                # Если было отмененное занятие в это время - обновляем его статус
                canceled_lessons = Lesson.objects.filter(
                    tutor=tutor,
                    datetime__gte=start_time,
                    datetime__lt=end_time,
                    status='canceled'
                )

                messages.success(request,
                                 f"Занятие успешно запланировано на {start_time.strftime('%d.%m.%Y %H:%M')}")
                return redirect('my_lessons')

        except Program.DoesNotExist:
            messages.error(request, "Выбранная программа не существует")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error creating lesson: {str(e)}", exc_info=True)
            messages.error(request, "Произошла ошибка при создании занятия. Пожалуйста, попробуйте позже.")

        # Если что-то пошло не так, возвращаем с ошибкой
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
