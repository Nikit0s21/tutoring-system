from django.core.exceptions import ValidationError
from users.models import Tutor
from django.db import models
from django.utils import timezone

class TimeSlot(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.tutor.user.get_full_name()} - {self.start_time.strftime('%d.%m %H:%M')}-{self.end_time.strftime('%H:%M')}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("Время окончания должно быть позже времени начала")

        if self.start_time < timezone.now():
            raise ValidationError("Нельзя создавать слоты в прошлом")