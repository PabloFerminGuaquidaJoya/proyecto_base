from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'maquinaria'

urlpatterns = [
    # Dashboard de maquinaria
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # CRUD de máquinas
    path('lista/', views.lista_maquinas_view, name='lista_maquinas'),
    path('crear/', views.crear_maquina_view, name='crear_maquina'),
    path('detalle/<int:pk>/', views.detalle_maquina_view, name='detalle_maquina'),
    path('editar/<int:pk>/', views.editar_maquina_view, name='editar_maquina'),
    path('eliminar/<int:pk>/', views.eliminar_maquina_view, name='eliminar_maquina'),

    # Estado de máquinas
    path('cambiar-estado/<int:pk>/', views.cambiar_estado_maquina, name='cambiar_estado'),
    path('historial/<int:pk>/', views.historial_maquina_view, name='historial_maquina'),

    # Categorías y proveedores
    path('categorias/', views.categorias_view, name='categorias'),
    path('categorias/crear/', views.crear_categoria_view, name='crear_categoria'),
    path('proveedores/', views.proveedores_view, name='proveedores'),
    path('proveedores/crear/', views.crear_proveedor_view, name='crear_proveedor'),

    # Alertas
    path('alertas/', views.alertas_view, name='alertas'),
    path('alertas/crear/', views.crear_alerta_view, name='crear_alerta'),
    path('alertas/resolver/<int:pk>/', views.resolver_alerta, name='resolver_alerta'),
    path('alertas/detalle/<int:pk>/', views.detalle_alerta_view, name='detalle_alerta'),

    # Mantenimiento
    path('mantenimiento/', views.mantenimiento_dashboard_view, name='mantenimiento_dashboard'),
    path('mantenimiento/programar/', views.programar_mantenimiento_view, name='programar_mantenimiento'),
    path('mantenimiento/programar/<int:pk>/', views.programar_mantenimiento_view, name='programar_mantenimiento_maquina'),

    # Importar/Exportar
    path('importar/', views.importar_maquinas_view, name='importar_maquinas'),
    path('exportar/', views.exportar_maquinas_view, name='exportar_maquinas'),

    # QR Codes
    path('qr/<int:pk>/', views.generar_qr_maquina, name='generar_qr'),
    path('qr-info/<str:codigo>/', views.info_qr_maquina, name='info_qr'),

    # Objetos — registro movido a inventario
    path('objetos/', views.lista_objetos_view, name='lista_objetos'),
    path('objetos/registrar/', lambda r: redirect('inventario:nueva_pieza'), name='registrar_objeto'),
    path('objetos/detalle/<int:pk>/', views.detalle_objeto_view, name='detalle_objeto'),
    path('objetos/editar/<int:pk>/', views.editar_objeto_view, name='editar_objeto'),
    path('objetos/eliminar/<int:pk>/', views.eliminar_objeto_view, name='eliminar_objeto'),

    # Uso de Maquinaria
    path('uso/', views.lista_uso_maquinaria_view, name='lista_uso_maquinaria'),
    path('uso/registrar/', views.registrar_uso_maquinaria_view, name='registrar_uso_maquinaria'),

    # API endpoints para AJAX
    path('api/buscar/', views.buscar_maquinas_api, name='api_buscar'),
    path('api/estadisticas/', views.estadisticas_maquinaria_api, name='api_estadisticas'),
    path('api/alertas-activas/', views.alertas_activas_api, name='api_alertas_activas'),
    path('api/maquina/<int:pk>/datos/', views.datos_maquina_api, name='api_datos_maquina'),
]