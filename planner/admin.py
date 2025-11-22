from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from .models import Service, Appointment

# ========== SERVICE ==========
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_min", "buffer_min", "price_eur", "color_swatch")
    list_editable = ("duration_min", "buffer_min", "price_eur")
    search_fields = ("name",)
    ordering = ("name",)
    fieldsets = (
        ("Osnovno", {"fields": ("name", "price_eur")}),
        ("Trajanje", {"fields": ("duration_min", "buffer_min")}),
        ("Prikaz",   {"fields": ("color",)}),
    )

    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;border-radius:4px;background:{};border:1px solid #ccc"></span> {}',
            obj.color, obj.color
        )
    color_swatch.short_description = "Boja"

    actions = ["napuni_default_usluge"]

    def napuni_default_usluge(self, request, queryset):
        defaults = [
            ("Šišanje", 45, 0, "25.00", "#667eea"),
            ("Bojanje", 90, 10, "60.00", "#f56565"),
            ("Pranje + Feniranje", 30, 0, "15.00", "#48bb78"),
            ("Tretman", 45, 5, "35.00", "#ed8936"),
        ]
        created = 0
        for name, dur, buf, price, color in defaults:
            obj, was_created = Service.objects.get_or_create(
                name=name,
                defaults={
                    "duration_min": dur,
                    "buffer_min": buf,
                    "price_eur": price,
                    "color": color,
                },
            )
            if was_created:
                created += 1
        self.message_user(request, f"Dodano {created} usluga.")
    napuni_default_usluge.short_description = "Dodaj zadane usluge"

# ========== APPOINTMENT ==========
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_display = (
        "date", "start_time", "end_time",
        "customer_name", "service_badge", "note_short",
        "created_at",
    )
    list_filter = ("date", "service")
    search_fields = ("customer_name", "note", "service__name")
    ordering = ("-date", "start_time")
    autocomplete_fields = ("service",)
    readonly_fields = ("end_time", "created_at")

    fieldsets = (
        (None, {"fields": ("customer_name", "service", "note")}),
        ("Vrijeme", {"fields": ("date", "start_time", "end_time")}),
        ("Sustav", {"fields": ("created_at",)}),
    )

    def service_badge(self, obj):
        return format_html(
            '<span style="padding:2px 8px;border-radius:10px;background:{};color:#fff;">{}</span>',
            obj.service.color, obj.service.name
        )
    service_badge.short_description = "Usluga"

    def note_short(self, obj):
        if not obj.note:
            return ""
        return (obj.note[:40] + "…") if len(obj.note) > 40 else obj.note
    note_short.short_description = "Napomena"

    # brzi filtri (danas / ovaj tjedan / budući)
    def get_search_results(self, request, queryset, search_term):
        """
        normalna pretraga + kratice:
        =today      današnji termini
        =week       termini ovog ISO tjedna
        =future     budući termini (od sutra)
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        term = (search_term or "").strip().lower()
        today = timezone.localdate()

        if term == "=today":
            queryset = queryset.filter(date=today)
        elif term == "=week":
            # ISO tjedan
            iso_year, iso_week, _ = today.isocalendar()
            # dohvaćamo sve datume pon-sub istog ISO tjedna
            from datetime import timedelta, date as ddate
            first = ddate.fromisocalendar(iso_year, iso_week, 1)
            last = first + timedelta(days=5)
            queryset = queryset.filter(date__range=[first, last])
        elif term == "=future":
            queryset = queryset.filter(date__gt=today)

        return queryset, use_distinct

    actions = ["kopiraj_u_idući_tjedan"]

    def kopiraj_u_idući_tjedan(self, request, queryset):
        """
        Kopiraj označene termine u isti dan/tjedan + 7 dana.
        """
        from datetime import timedelta
        count = 0
        for ap in queryset:
            new_date = ap.date + timedelta(days=7)
            # pokušaj insert (ako se preklapa, clean() će dići ValidationError)
            try:
                Appointment.objects.create(
                    service=ap.service,
                    customer_name=ap.customer_name,
                    date=new_date,
                    start_time=ap.start_time,
                    note=ap.note,
                )
                count += 1
            except Exception as e:
                # ignoriramo preklapanje, možemo i message_user s warningom
                continue
        self.message_user(request, f"Kopirano {count} termina u idući tjedan.")
    kopiraj_u_idući_tjedan.short_description = "Kopiraj izabrane u idući tjedan"
