from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # naš GET logout (bez CSRF-a) – ako si dodao
    path("accounts/logout/", accounts_views.quick_logout, name="logout"),

    # ✅ signup ruta (username+password)
    path("accounts/signup/", accounts_views.signup_view, name="signup"),

    # Django auth rute: /accounts/login, /accounts/password_reset, ...
    path("accounts/", include("django.contrib.auth.urls")),

    # tvoj kalendar
    path("", include("planner.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)