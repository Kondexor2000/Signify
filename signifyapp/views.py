import time
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.db import transaction
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone
from .models import Invoice, Light, Component
from .forms import InvoiceForm
from django.contrib import messages

# Utworzenie kont klientów Signify
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('notifications')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'Jesteś już zalogowany.')
            return redirect('notifications')
        return super().dispatch(request, *args, **kwargs)

# Wylogowanie klientów Signify
class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = 'login_existing'

# Edycja danych użytkownika
class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('notifications')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Nie jesteś zalogowany.')
            return redirect('login_existing')
        return super().dispatch(request, *args, **kwargs)

# Usunięcie konta użytkownika
class DeleteAccountView(LoginRequiredMixin, DeleteView):
    template_name = 'delete_account.html'
    success_url = reverse_lazy('login_existing')

    def get_object(self, queryset=None):
        # Upewnienie się, że użytkownik usuwa swoje własne konto
        user = self.request.user
        if user.is_authenticated:
            return user
        else:
            raise Http404("Nie jesteś zalogowany.")

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Wystąpił błąd: {str(e)}")
            return redirect('delete_account')

#Wystawienie rachunków
class AddInvoiceView(LoginRequiredMixin, CreateView):
    form_class = InvoiceForm
    template_name = 'comment.html'
    success_url = reverse_lazy('post_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#Przeglądarka niezapłaconych rachunków
def read_invoices(request):
    user = request.user
    comments = Invoice.objects.filter(is_paid=False , user=user)
    return render(request, 'comment.html', {'comments': comments})

#Zarządzanie rachunkami
def read_invoices_by_admin(request):
    comments = Invoice.objects.all()
    return render(request, 'comment.html', {'comments': comments})

# Aktualizacja rachunku
class UpdateInvoiceView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'update_invoice.html'
    success_url = reverse_lazy('post_detail')

# Usuwanie rachunku
class DeleteInvoiceView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'delete_invoice.html'
    success_url = reverse_lazy('post_detail')

# Algorytm wyłączenia sprzętów oświetleniowych po upływie terminu płatności
# Automatyzacja kontroli płatności rachunków
@transaction.atomic
def check_payment_deadline(request):
    if request.user.is_authenticated:
        overdue_invoices = Invoice.objects.filter(user=request.user, payment_due_date__lt=timezone.now().date(), is_paid=False)
        for invoice in overdue_invoices:
            if invoice.last > invoice.payment_due_date:
                try:
                    light = Light.objects.get(invoice=invoice)
                    light.is_on = False
                    light.user = request.user  # Dodaj to pole
                    light.save()
                    raport = "Wyłączyliśmy światło, ponieważ nie zapłaciłeś rachunku w terminie"
                except Light.DoesNotExist:
                    pass
        else:
            raport = "Rachunki zapłacone! Światło jest w twoich rękach"
        return render(request, 'template.html', {'components': raport})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')

# Algorytm reklamy bardziej ekologicznych sprzętów oświetleniowych skierowanych do gospodarstw domowych z największym zużyciem prądu w oświetleniach
@transaction.atomic
def display_records_with_average_above_10(request):
    if request.user.is_authenticated:
        components = Component.objects.filter(user=request.user, average__gt=10)
        if components.exists():
            raport = 'Proponujemy bardziej oszczędne światło'
        else:
            raport = "Gratulujemy oszczędności światła"
        return render(request, 'template_with_records.html', {'components': raport})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')

# Algorytm zastosowania algebry liniowej i statystyki w automatyzacji obliczeń zużytych prądów przez sprzęty oświetleniowe
# Obliczenie średniej zużytych prądów (Suma zużytych prądów przez liczbę serii)
@transaction.atomic
def index(request):
    if request.user.is_authenticated:
        component, created = Component.objects.get_or_create(user=request.user, defaults={'series': 0, 'time': 0, 'average': 0})
        
        start_time = request.session.get('start_time')  # Pobieramy czas rozpoczęcia z sesji

        if 'start' in request.POST:
            if start_time is None:
                start_time = time.time()
                request.session['start_time'] = start_time  # Zapisujemy czas rozpoczęcia do sesji
        elif 'stop' in request.POST:
            if start_time is not None:
                end_time = time.time()
                component.time += end_time - start_time
                component.series += 1
                component.save()
                start_time = None
                del request.session['start_time']  # Usuwamy czas rozpoczęcia z sesji

        if component.series != 0:
            result = component.time / component.series
        else:
            result = 0

        return render(request, 'index.html', {'result': result})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')