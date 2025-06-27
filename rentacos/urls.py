from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='inicio.html'), name='home'),  # tu página de inicio
    path('', include('apps.alquiler.urls')),  # rutas de tu app alquiler
    path('flota/', include('apps.flota.urls')),  # rutas de la app flota
    path('mantenimiento/', include('apps.mantenimiento.urls')),  # rutas de la app mantenimiento
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)