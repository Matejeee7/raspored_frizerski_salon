from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_today, name="calendar_today"),
    path("week/<int:year>/<int:week>/", views.calendar_week_view, name="calendar_week"),
    path("appointments/create/", views.create_appointment, name="create_appointment"),
    path('appointments/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path("appointments/<int:appointment_id>/delete/", views.delete_appointment, name="delete_appointment"),
]
