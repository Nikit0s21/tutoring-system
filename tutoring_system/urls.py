"""
URL configuration for tutoring_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from users.views import VerificationRequestCreateView, VerificationRequestListView, ProgramListView, ProgramCreateView, ProgramUpdateView, ProgramDeleteView, ProgramDetailView
from bookings.views import tutor_search, TutorDetailView,  LessonDetailView, MyLessonsView, CancelLessonView, CompleteLessonView, GradeLessonView
from schedule.views import (TutorScheduleView, TimeSlotCreateView,
                          TimeSlotUpdateView, TimeSlotDeleteView)

from tutoring_system import settings



urlpatterns = [

    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    # Верификация
    path('verification/', VerificationRequestCreateView.as_view(), name='verification_request'),
    path('admin/verification/', VerificationRequestListView.as_view(), name='verification_list'),
    path('admin/', admin.site.urls),

    # Поиск и запись
    path('tutors/', tutor_search, name='tutor_search'),
    path('tutors/<int:pk>/', TutorDetailView.as_view(), name='tutor_detail'),

    # Расписание
    path('schedule/', TutorScheduleView.as_view(), name='tutor_schedule'),
    path('schedule/add/', TimeSlotCreateView.as_view(), name='time_slot_create'),
    path('schedule/<int:pk>/edit/', TimeSlotUpdateView.as_view(), name='time_slot_update'),
    path('schedule/<int:pk>/delete/', TimeSlotDeleteView.as_view(), name='time_slot_delete'),

    path('my-lessons/', MyLessonsView.as_view(), name='my_lessons'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/<int:pk>/cancel/', CancelLessonView.as_view(), name='cancel_lesson'),
    path('lesson/<int:pk>/complete/', CompleteLessonView.as_view(), name='complete_lesson'),
    path('lesson/<int:pk>/grade/', GradeLessonView.as_view(), name='grade_lesson'),
    path('programs/', include([
        path('', ProgramListView.as_view(), name='program_list'),
        path('new/', ProgramCreateView.as_view(), name='program_create'),
        path('<int:pk>/edit/', ProgramUpdateView.as_view(), name='program_update'),
        path('<int:pk>/delete/', ProgramDeleteView.as_view(), name='program_delete'),
        path('<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),


])),
    path('reports/', include('reports.urls', namespace='reports')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
