from django import forms
from django.utils import timezone


class TutorSearchForm(forms.Form):
    specialization = forms.CharField(required=False)
    min_rating = forms.DecimalField(required=False, min_value=0, max_value=5)
    is_verified = forms.BooleanField(required=False)

class BookingForm(forms.Form):
    class BookingForm(forms.Form):
        start_time = forms.DateTimeField(
            widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            label="Выберите время начала"
        )
        duration = forms.TypedChoiceField(
            choices=[(30, '30 минут'), (60, '1 час'), (90, '1.5 часа')],
            coerce=int,
            label="Продолжительность"
        )
        topic = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={'placeholder': 'Тема занятия'}),
            label="Тема"
        )
