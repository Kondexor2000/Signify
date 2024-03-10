from django.contrib import admin
from .models import Invoice

# Register your models here.

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_due_date', 'user')
    list_filter = ('payment_due_date', 'user')
    search_fields = ('id', 'payment_due_date', 'user__username')  # Przykład wyszukiwania po nazwie użytkownika