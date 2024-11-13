from django.db import models
from django.contrib.auth.models import User

#Rachunki zużytych prądów przez sprzęty oświetleniowe
class Invoice(models.Model):
    payment_due_date = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    last = models.DateField(auto_now_add=True)

#Komputerowe włączanie i wyłączanie sprzętów oświetleniowych
class Light(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    is_on = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

#Wzór na obliczanie średniej zużytych prądów
class Component(models.Model):
    series = models.IntegerField(default=0)
    time = models.FloatField(default=0.0)
    average = models.FloatField(default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Upewnij się, że `series` nie jest zerowe, aby uniknąć błędu dzielenia przez zero
        if self.series > 0:
            self.average = self.time / self.series
        else:
            self.average = 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Component for {self.user.username}: series={self.series}, average={self.average}"
