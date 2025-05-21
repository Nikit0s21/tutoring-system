from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import VerificationRequest, Program
from .forms import UserRegisterForm, StudentProfileForm, TutorProfileForm, ProgramForm
from .models import Student, Tutor


def home(request):
    return render(request, 'home.html')
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Создаем профиль в зависимости от типа пользователя
            if user.user_type == 'student':
                Student.objects.create(user=user)
            elif user.user_type == 'tutor':
                Tutor.objects.create(user=user)

            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.user.user_type == 'student':
        profile_form = StudentProfileForm(instance=request.user.student)
    elif request.user.user_type == 'tutor':
        profile_form = TutorProfileForm(instance=request.user.tutor)
    else:
        return redirect('home')

    if request.method == 'POST':
        if request.user.user_type == 'student':
            profile_form = StudentProfileForm(request.POST, instance=request.user.student)
        elif request.user.user_type == 'tutor':
            profile_form = TutorProfileForm(request.POST, instance=request.user.tutor)

        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')

    return render(request, 'users/profile.html', {'profile_form': profile_form})

from django.urls import reverse_lazy

class VerificationRequestCreateView(LoginRequiredMixin, CreateView):
    model = VerificationRequest
    fields = ['documents']
    template_name = 'users/verification_request.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.instance.tutor = self.request.user.tutor
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'tutor')


class VerificationRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = VerificationRequest
    template_name = 'users/verification_list.html'
    context_object_name = 'verification_requests'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return VerificationRequest.objects.select_related('tutor__user').order_by('-submitted_at')

    def post(self, request, *args, **kwargs):
        if 'approve' in request.POST:
            return self._process_verification(request, 'approved')
        elif 'reject' in request.POST:
            return self._process_verification(request, 'rejected')
        return self.get(request, *args, **kwargs)

    def _process_verification(self, request, status):
        request_id = request.POST.get('request_id')
        verification_request = get_object_or_404(VerificationRequest, id=request_id)

        verification_request.status = status
        verification_request.reviewed_by = request.user
        verification_request.reviewed_at = timezone.now()
        verification_request.save()

        if status == 'approved':
            verification_request.tutor.is_verified = True
            verification_request.tutor.save()
            messages.success(request, 'Запрос успешно одобрен!')
        else:
            messages.success(request, 'Запрос отклонен.')

        return redirect('verification_list')

class ProgramDetailView(DetailView):
    model = Program
    template_name = 'users/program_detail.html'
    context_object_name = 'program'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.object
        context['tutor'] = program.tutor
        context['lessons_count'] = program.lessons.count()
        context['average_rating'] = program.lessons.aggregate(
            Avg('studentlesson__grade')
        )['studentlesson__grade__avg']
        return context

class ProgramCreateView(LoginRequiredMixin, CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'users/program_form.html'
    success_url = reverse_lazy('program_list')

    def form_valid(self, form):
        form.instance.tutor = self.request.user.tutor
        return super().form_valid(form)

class ProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = 'users/program_form.html'
    success_url = reverse_lazy('program_list')

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user.tutor)

class ProgramDeleteView(LoginRequiredMixin, DeleteView):
    model = Program
    template_name = 'users/program_confirm_delete.html'
    success_url = reverse_lazy('program_list')

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user.tutor)

class ProgramListView(LoginRequiredMixin, ListView):
    model = Program
    template_name = 'users/program_list.html'
    context_object_name = 'programs'

    def get_queryset(self):
        return Program.objects.filter(tutor=self.request.user.tutor).order_by('-created_at')