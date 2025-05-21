from django import forms
from django.core.exceptions import ValidationError
from schedule.models import TimeSlot
from django.utils import timezone


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        tutor = self.instance.tutor if self.instance else None

        if not start_time or not end_time:
            return cleaned_data


        if end_time <= start_time:
            raise ValidationError("Время окончания должно быть позже времени начала")


        if start_time < timezone.now():
            raise ValidationError("Нельзя создавать слоты в прошлом")


        if tutor:
            overlapping_slots = TimeSlot.objects.filter(
                tutor=tutor,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if self.instance:
                overlapping_slots = overlapping_slots.exclude(pk=self.instance.pk)

            if overlapping_slots.exists():
                raise ValidationError(
                    "Этот слот пересекается с существующими: " +
                    ", ".join(f"{slot.start_time} - {slot.end_time}" for slot in overlapping_slots)
                )

        return cleaned_data