from datetime import timezone

from django.contrib import admin
from .models import VerificationRequest, CustomUser, Tutor, Student, Program, Lesson, StudentLesson
from schedule.models import TimeSlot


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['tutor', 'status', 'submitted_at']
    list_filter = ['status']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        # Обновляем статус верификации у репетиторов
        Tutor.objects.filter(
            id__in=queryset.values_list('tutor', flat=True)
        ).update(is_verified=True)
    approve_requests.short_description = "Одобрить выбранные запросы"

    def reject_requests(self, request, queryset):
        queryset.update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
    reject_requests.short_description = "Отклонить выбранные запросы"

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'tutor', 'price_per_hour', 'created_at')
    list_filter = ('tutor',)
    search_fields = ('name', 'description')



@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name')
    list_filter = ('user_type',)

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_verified')
    list_filter = ('specialization', 'is_verified')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'education_level')
    list_filter = ('education_level',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'tutor', 'program', 'datetime', 'status')
    list_filter = ('status', 'tutor')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'start_time', 'end_time')
    list_filter = ('tutor',)

@admin.register(StudentLesson)
class StudentLessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'grade')
    list_filter = ('grade',)