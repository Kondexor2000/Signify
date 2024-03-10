import time
from .models import Invoice, Light, Component
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

#Logowanie klientów Signify
def login_existing(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('notifications')
    return render(request, 'login.html')

#Utworzenie kont klientów Signify
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('notifications')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

#Wylogowanie klientów Signify
def logout_view(request):
    logout(request)
    return redirect('login_existing')

#Algorytm wyłączenia sprzętów oświetleniowych po upływie terminu płatności
#Automatyzacja kontroli płatności rachunków
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
        return redirect('login_existing')

#Algorytm reklamy bardziej ekologicznych sprzętów oświetleniowych skierowanych do gospodarstw domowych z największym zużyciem prądu w oświetleniach
def display_records_with_average_above_10(request):
    if request.user.is_authenticated:
        components = Component.objects.filter(user=request.user, average__gt=10)
        if components.exists():
            raport = 'Proponujemy bardziej oszczędne światło'
        else:
            raport = "Gratulujemy oszczędności światła"
        return render(request, 'template_with_records.html', {'components': raport})
    else:
        return redirect('login_existing')

#Algorytm zastosowania algebry liniowej i statystyki w automatyzacji obliczeń zużytych prądów przez sprzęty oświetleniowe
#Obliczenie średniej zużytych prądów (Suma zużytych prądów przez liczbę serii)
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
        return redirect('login_existing')