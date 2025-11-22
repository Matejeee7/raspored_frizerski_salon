from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, time

# Radno vrijeme (po potrebi promijeni)
HOURS_START = 7
HOURS_END   = 21

class Service(models.Model):
    name = models.CharField(max_length=80)
    duration_min = models.PositiveIntegerField(default=30)
    color = models.CharField(max_length=7, default="#4caf50")  # #RRGGBB
    price_eur = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    buffer_min = models.PositiveIntegerField(default=0)
    def __str__(self): return self.name

class Appointment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=120, default="")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(editable=False)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def clean(self):
        # izračun kraja po trajanju + bufferu
        total = self.service.duration_min + self.service.buffer_min
        dt_start = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time),
            timezone.get_current_timezone()
        )
        dt_end = dt_start + timedelta(minutes=total)
        self.end_time = dt_end.time()

        # radno vrijeme
        if not (time(hour=HOURS_START) <= self.start_time < time(hour=HOURS_END)):
            raise ValidationError("Termin počinje izvan radnog vremena (09–19).")
        if not (time(hour=HOURS_START) < self.end_time <= time(hour=HOURS_END)):
            raise ValidationError("Termin završava izvan radnog vremena (09–19).")

        # preklapanje (isti dan)
        clash = Appointment.objects.filter(
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            clash = clash.exclude(pk=self.pk)
        if clash.exists():
            raise ValidationError("Termin se preklapa s postojećim.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
