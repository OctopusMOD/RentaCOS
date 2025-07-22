from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # Tema Grappelli antes del admin
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Esto te da login/logout/reset/cambio de contraseña
    path('', TemplateView.as_view(template_name='inicio.html'), name='home'),
    path('alquiler/', include('apps.alquiler.urls')),
    path('flota/', include('apps.flota.urls')),
    path('mantenimiento/', include('apps.mantenimiento.urls')),
]

# Soporte para archivos MEDIA y STATIC en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)