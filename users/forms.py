from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Student, Tutor, Lesson, StudentLesson, Program


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=17, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'first_name', 'last_name', 'middle_name', 'password1', 'password2',
                  'user_type']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['education_level']


class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['qualification', 'specialization']


class CompleteLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['tutor_notes']
        widgets = {
            'tutor_notes': forms.Textarea(attrs={'rows': 3})
        }

class GradeLessonForm(forms.ModelForm):
    class Meta:
        model = StudentLesson
        fields = ['grade', 'feedback']
        widgets = {
            'grade': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'feedback': forms.Textarea(attrs={'rows': 3})
        }

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'description', 'price_per_hour']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите программу обучения...'}),
            'price_per_hour': forms.NumberInput(attrs={
                'min': 0,
                'step': 100,
                'placeholder': 'Стоимость за 1 час занятий'
            })
        }
        labels = {
            'name': 'Название программы',
            'description': 'Описание',
            'price_per_hour': 'Стоимость (₽/час)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_per_hour'].widget.attrs.update({'class': 'form-control'})