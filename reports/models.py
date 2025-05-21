from django.db import models
from django.db.models import Count, Sum, Avg, Case, When, IntegerField, Q, F
from users.models import Program, Lesson

class ReportManager(models.Manager):
    def program_revenue(self, tutor, start_date, end_date):
        return Program.objects.filter(
            tutor=tutor,
            lessons__datetime__range=(start_date, end_date),
            lessons__status='completed'
        ).annotate(
            total_revenue=Sum('lessons__duration') * F('price_per_hour') / 60,
            lessons_count=Count('lessons')
        ).order_by('-total_revenue')

    def lessons_stats(self, tutor, start_date, end_date):
        return Lesson.objects.filter(
            tutor=tutor,
            datetime__range=(start_date, end_date)
        ).aggregate(
            completed=Count('id', filter=Q(status='completed')),
            canceled=Count('id', filter=Q(status='canceled')),
            avg_fill=Avg(Case(
                When(status='completed', then=1),
                When(status='canceled', then=0),
                output_field=IntegerField()
            ))
        )

    def program_popularity(self, tutor):
        return Program.objects.filter(
            tutor=tutor
        ).annotate(
            popularity=Count('lessons'),
            completion_rate=Avg(Case(
                When(lessons__status='completed', then=1),
                When(lessons__status='canceled', then=0),
                output_field=IntegerField()
            ))
        ).order_by('-popularity')