"""
URL configuration for app_prototipo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.http import FileResponse, Http404
import os

def redirect_to_login(request):
    return redirect('/usuarios/login/')

def descargar_manual(request):
    """Vista para descargar el manual de usuario"""
    # Ruta al archivo del manual
    # INSTRUCCIÓN: Coloca tu archivo PDF del manual en:
    # C:\INFORMACION\Desktop\prototipo_0.1\myworld\app_prototipo\media\manuales\manual_usuario.pdf

    file_path = os.path.join(settings.MEDIA_ROOT, 'manuales', 'manual_usuario.pdf')

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Manual_Usuario_SENA_Maquinaria.pdf"'
        return response
    else:
        raise Http404("El manual de usuario no está disponible en este momento.")

def descargar_manual_app(request):
    """Vista para descargar el manual completo de la aplicación"""
    # INSTRUCCIÓN: Coloca tu archivo PDF del manual de la app en:
    # C:\INFORMACION\Desktop\prototipo_0.1\myworld\app_prototipo\media\manuales\manual_tecnico_app.pdf

    file_path = os.path.join(settings.MEDIA_ROOT, 'manuales', 'manual_tecnico_app.pdf')

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Manual_Completo_App_SENA_Maquinaria.pdf"'
        return response
    else:
        raise Http404("El manual de la aplicación no está disponible en este momento.")

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root to login
    path('', redirect_to_login, name='home'),

    # Manuales
    path('descargar-manual/', descargar_manual, name='descargar_manual'),
    path('descargar-manual-app/', descargar_manual_app, name='descargar_manual_app'),

    # App URLs
    path('usuarios/', include('usuarios.urls')),
    path('maquinaria/', include('maquinaria.urls')),
    path('reportes/', include('reportes.urls')),
    path('documentos/', include('documentos.urls')),
    path('inventario/', include('inventario.urls')),
    path('vision/', include('vision.urls')),
    path('sistema/', include('sistema.urls')),

    # API URLs
    path('api/', include('api.urls')),
    path('api/auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'sistema.views.handler404'
handler500 = 'sistema.views.handler500'