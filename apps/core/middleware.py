# apps/core/middleware.py

from django.conf import settings
from django.shortcuts import redirect

# Lista de rutas exentas del login obligatorio
EXEMPT_URLS = [
    '/accounts/login/',
    '/accounts/logout/',
    '/accounts/password_reset/',
    '/accounts/password_reset/done/',
    '/accounts/reset/',  # esto cubre los links con token, puedes ajustarlo si usas otro path
    '/admin/',
    '/',  # si quieres dejar el home público, si no, bórralo
]

class LoginRequiredMiddleware:
    """
    Middleware que restringe el acceso a usuarios autenticados
    excepto para las rutas exentas definidas en EXEMPT_URLS.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        # Permite el acceso si la ruta es exenta o el usuario está autenticado
        if not request.user.is_authenticated:
            if not any(path.startswith(url) for url in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)