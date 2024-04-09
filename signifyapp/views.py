import time
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.db import transaction
from django.template import TemplateDoesNotExist
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone
from .models import Invoice, Light, Component
from .forms import InvoiceForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.template.loader import get_template

# Funkcja do sprawdzania istnienia szablonu HTML
def check_template(template_name, request):
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        messages.error(request, 'Brak pliku HTML')
        return False
    return True

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        if not check_template(self.template_name, self.request):
            return self.form_invalid(form)

        remember_me = form.cleaned_data.get('remember_me', False)
        if remember_me:
            self.request.session.set_expiry(1209600)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('index')

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('index')

        if request.user.is_authenticated:
            messages.error(request, 'Jesteś już zalogowany.')
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)

class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = 'login_existing'

class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserChangeForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('notifications')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('login_existing')

        if not request.user.is_authenticated:
            messages.error(request, 'Nie jesteś zalogowany.')
            return redirect('login_existing')
        return super().dispatch(request, *args, **kwargs)

class DeleteAccountView(LoginRequiredMixin, DeleteView):
    template_name = 'delete_account.html'
    success_url = reverse_lazy('login_existing')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('post_detail')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
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

class AddInvoiceView(LoginRequiredMixin, CreateView):
    form_class = InvoiceForm
    template_name = 'comment.html'
    success_url = reverse_lazy('post_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('post_detail')

        return super().dispatch(request, *args, **kwargs)

def read_invoices(request):
    template_name = 'comment.html'
    if not check_template(template_name, request):
        return redirect('gdzieś_indziej')

    user = request.user
    comments = Invoice.objects.filter(is_paid=False, user=user)
    return render(request, template_name, {'comments': comments})

def read_invoices_by_admin(request):
    template_name = 'comment.html'
    if not check_template(template_name, request):
        return redirect('gdzieś_indziej')

    comments = Invoice.objects.all()
    return render(request, template_name, {'comments': comments})

class UpdateInvoiceView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'update_invoice.html'
    success_url = reverse_lazy('post_detail')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('post_detail')

        return super().dispatch(request, *args, **kwargs)

class DeleteInvoiceView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'delete_invoice.html'
    success_url = reverse_lazy('post_detail')

    def dispatch(self, request, *args, **kwargs):
        if not check_template(self.template_name, request):
            return redirect('post_detail')

        return super().dispatch(request, *args, **kwargs)

@transaction.atomic
def check_payment_deadline(request):
    template_name = 'comment.html'
    if not check_template(template_name, request):
        return redirect('gdzieś_indziej')

    if request.user.is_authenticated:
        template_name = 'template.html'
        if not check_template(template_name, request):
            return redirect('gdzieś_indziej')

        overdue_invoices = Invoice.objects.filter(user=request.user, payment_due_date__lt=timezone.now().date(), is_paid=False)
        for invoice in overdue_invoices:
            if invoice.last > invoice.payment_due_date:
                try:
                    light = Light.objects.get(invoice=invoice)
                    light.is_on = False
                    light.user = request.user
                    light.save()
                    raport = "Wyłączyliśmy światło, ponieważ nie zapłaciłeś rachunku w terminie"
                except Light.DoesNotExist:
                    pass
        else:
            raport = "Rachunki zapłacone! Światło jest w twoich rękach"
        return render(request, template_name, {'components': raport})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')

@transaction.atomic
def display_records_with_average_above_10(request):
    if request.user.is_authenticated:
        template_name = 'template_with_records.html'
        if not check_template(template_name, request):
            return redirect('login_existing')

        components = Component.objects.filter(user=request.user, average__gt=10)
        if components.exists():
            raport = 'Proponujemy bardziej oszczędne światło'
        else:
            raport = "Gratulujemy oszczędności światła"
        return render(request, 'template_with_records.html', {'components': raport})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')

@transaction.atomic
def index(request):
    if request.user.is_authenticated:
        template_name = 'index.html'
        if not check_template(template_name, request):
            return redirect('login_existing')

        component, created = Component.objects.get_or_create(user=request.user, defaults={'series': 0, 'time': 0, 'average': 0})
        
        start_time = request.session.get('start_time')

        if 'start' in request.POST:
            if start_time is None:
                start_time = time.time()
                request.session['start_time'] = start_time
        elif 'stop' in request.POST:
            if start_time is not None:
                end_time = time.time()
                component.time += end_time - start_time
                component.series += 1
                component.save()
                start_time = None
                del request.session['start_time']

        if component.series != 0:
            result = component.time / component.series
        else:
            result = 0

        return render(request, template_name, {'result': result})
    else:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login_existing')