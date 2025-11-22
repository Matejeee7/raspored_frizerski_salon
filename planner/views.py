from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date, timedelta, datetime
from .models import Appointment, Service, HOURS_START, HOURS_END
from .forms import AppointmentForm

# Povećali smo visinu sata da kartice komotno stanu
HOUR_PX = 80  # px po satu


def get_week_dates(year, week):
    """Vraća listu datuma za dani tjedan (ponedjeljak do subota)."""
    first_day = datetime.fromisocalendar(year, week, 1).date()  # ponedjeljak
    return [first_day + timedelta(days=i) for i in range(6)]    # pon–sub


@login_required
def calendar_today(request):
    today = date.today()
    year, week, _ = today.isocalendar()
    return redirect("calendar_week", year=year, week=week)


@login_required
def calendar_week_view(request, year=None, week=None):
    # Ako nije specificiran year/week, koristi trenutni tjedan
    if year is None or week is None:
        today = date.today()
        year, week, _ = today.isocalendar()

    # Datumi tjedna
    days = get_week_dates(year, week)
    start_date, end_date = days[0], days[-1]

    # Termini
    appointments = (
        Appointment.objects.filter(date__range=[start_date, end_date])
        .select_related("service")
        .order_by("date", "start_time")
    )

    # Grupiranje po danima
    appointments_by_day = {d: [] for d in days}
    for a in appointments:
        appointments_by_day[a.date].append(a)

    # Blokovi za prikaz (top/height u px) — pretvorimo u int radi sigurnosti
    day_columns = []
    for day in days:
        blocks = []
        for a in appointments_by_day[day]:
            start_minutes = a.start_time.hour * 60 + a.start_time.minute
            end_minutes = a.end_time.hour * 60 + a.end_time.minute
            top_px = int(((start_minutes - (HOURS_START * 60)) / 60) * HOUR_PX)
            height_px = max(6, int(((end_minutes - start_minutes) / 60) * HOUR_PX) - 4)
            blocks.append(
                {
                    "appointment": a,
                    "top": top_px,
                    "height": height_px,
                    "color": a.service.color if a.service and a.service.color else "#667eea",
                }
            )
        day_columns.append({"date": day, "blocks": blocks})

    # Navigacija
    prev_week_date = start_date - timedelta(days=7)
    next_week_date = start_date + timedelta(days=7)
    prev_year, prev_week, _ = prev_week_date.isocalendar()
    next_year, next_week, _ = next_week_date.isocalendar()

    context = {
        "year": year,
        "week": week,
        "days": days,
        "hours": list(range(HOURS_START, HOURS_END)),
        "columns": day_columns,
        "HOUR_PX": HOUR_PX,
        "prev_link": reverse("calendar_week", kwargs={"year": prev_year, "week": prev_week}),
        "next_link": reverse("calendar_week", kwargs={"year": next_year, "week": next_week}),
        "form": AppointmentForm(),
    }
    return render(request, "planner/calendar_week.html", context)


@login_required
def create_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save()
            messages.success(request, f"Termin za {appt.customer_name} je kreiran.")
        else:
            messages.error(request, "Greška pri kreiranju termina.")
        next_url = request.GET.get("next") or reverse("calendar_today")
        return redirect(next_url)
    return redirect("calendar_today")


@login_required
def update_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appt)
        if form.is_valid():
            appt = form.save()
            messages.success(request, f"Izmjene spremljene za {appt.customer_name}.")
        else:
            messages.error(request, "Greška pri spremanju izmjena.")
        next_url = request.GET.get("next") or reverse("calendar_today")
        return redirect(next_url)
    # GET: vraćamo JSON (opcionalno, nije obavezno koristiti)
    return JsonResponse(
        {
            "id": appt.id,
            "customer_name": appt.customer_name,
            "service": appt.service_id,
            "date": appt.date.isoformat(),
            "start_time": appt.start_time.strftime("%H:%M"),
            "note": appt.note,
        }
    )


@require_POST
@login_required
def delete_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)
    appt.delete()
    # Ako je AJAX, vrati JSON; inače redirectaj
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})
    messages.success(request, "Termin je obrisan.")
    return redirect(request.META.get("HTTP_REFERER", reverse("calendar_today")))
