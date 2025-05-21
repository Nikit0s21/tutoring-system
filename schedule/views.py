from django.core.exceptions import ValidationError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import TimeSlotForm
from .models import TimeSlot



class TutorScheduleView(LoginRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'schedule/tutor_schedule.html'
    context_object_name = 'time_slots'

    def get_queryset(self):
        return TimeSlot.objects.filter(
            tutor=self.request.user.tutor,
            start_time__gte=timezone.now()
        ).order_by('start_time')


class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = 'schedule/time_slot_form.html'
    success_url = reverse_lazy('tutor_schedule')

    def form_valid(self, form):
        form.instance.tutor = self.request.user.tutor
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'tutor'):
            kwargs['instance'] = TimeSlot(tutor=self.request.user.tutor)
        return kwargs

class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = 'schedule/time_slot_form.html'
    success_url = reverse_lazy('tutor_schedule')

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user.tutor)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TimeSlotDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeSlot
    template_name = 'schedule/time_slot_confirm_delete.html'
    success_url = reverse_lazy('tutor_schedule')

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user.tutor)