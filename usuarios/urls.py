from django.urls import path, include
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Recuperación de contraseña
    path('recuperar-password/', views.recuperar_password_view, name='recuperar_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),

    # Dashboard y home después del login
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),

    # Gestión de usuarios (solo admin)
    path('lista/', views.lista_usuarios_view, name='lista'),
    path('crear/', views.crear_usuario_view, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario_view, name='editar'),
    path('detalle/<int:pk>/', views.detalle_usuario_view, name='detalle'),
    path('cambiar-estado/<int:pk>/', views.cambiar_estado_usuario, name='cambiar_estado'),

    # Configuración
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('registrar-rostro/', views.registrar_rostro_page_view, name='registrar_rostro_page'),

    # API endpoints para AJAX
    path('api/buscar/', views.buscar_usuarios_api, name='api_buscar'),
    path('api/estadisticas/', views.estadisticas_usuarios_api, name='api_estadisticas'),

    # API Reconocimiento facial
    path('api/registrar-rostro/', views.registrar_rostro_view, name='api_registrar_rostro'),
    path('api/login-facial/', views.login_facial_view, name='api_login_facial'),
    path('api/verificar-reconocimiento/', views.verificar_tiene_reconocimiento_facial, name='api_verificar_reconocimiento'),
    path('api/eliminar-reconocimiento/', views.eliminar_reconocimiento_facial, name='api_eliminar_reconocimiento'),
]