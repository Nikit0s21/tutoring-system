from django.urls import path
from .views import TutorDashboardView, TutorReportsAPI

app_name = 'reports'

urlpatterns = [
    path('dashboard/', TutorDashboardView.as_view(), name='dashboard'),
    path('api/tutor-reports/', TutorReportsAPI.as_view(), name='tutor-reports-api'),

]