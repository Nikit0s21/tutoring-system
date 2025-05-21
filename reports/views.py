from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q, F, ExpressionWrapper, FloatField
from users.models import Program, Lesson


class TutorReportsAPI(APIView):
    def get(self, request):
        if not hasattr(request.user, 'tutor'):
            return Response({'error': 'Доступ только для репетиторов'}, status=403)

        tutor = request.user.tutor
        time_range = request.GET.get('range', 'month')

        # Определяем период
        end_date = timezone.now()
        if time_range == 'week':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)

        # 1. Доход по программам
        program_revenue = Program.objects.filter(
            tutor=tutor,
            lessons__datetime__range=(start_date, end_date),
            lessons__status='completed'
        ).annotate(
            total_revenue=ExpressionWrapper(
                Sum(F('lessons__duration') * F('price_per_hour')) / 60,
                output_field=FloatField()
            ),
            lessons_count=Count('lessons')
        ).order_by('-total_revenue').values('id', 'name', 'price_per_hour', 'total_revenue', 'lessons_count')

        # 2. Статистика занятий
        lessons_stats = Lesson.objects.filter(
            tutor=tutor,
            datetime__range=(start_date, end_date)
        ).aggregate(
            completed=Count('id', filter=Q(status='completed')),
            canceled=Count('id', filter=Q(status='canceled')),
            total=Count('id')
        )
        lessons_stats['fill_rate'] = round(
            (lessons_stats['completed'] / lessons_stats['total'] * 100)
            if lessons_stats['total'] > 0 else 0,
            1
        )

        # 3. Популярность программ (переработанный запрос)
        programs = Program.objects.filter(tutor=tutor)
        program_popularity = []

        for program in programs:
            lessons = program.lessons.all()
            total = lessons.count()
            completed = lessons.filter(status='completed').count()

            program_popularity.append({
                'id': program.id,
                'name': program.name,
                'popularity': total,
                'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
            })

        # Сортируем по популярности
        program_popularity.sort(key=lambda x: x['popularity'], reverse=True)

        return Response({
            'program_revenue': list(program_revenue),
            'lessons_stats': lessons_stats,
            'program_popularity': program_popularity,
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        })


class TutorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/tutor_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'tutor'):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)