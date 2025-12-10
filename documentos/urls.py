from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    # Repositorio principal
    path('', views.repositorio_view, name='repositorio'),
    path('buscar/', views.buscar_documentos_view, name='buscar_documentos'),

    # CRUD de documentos
    path('subir/', views.subir_documento_view, name='subir_documento'),
    path('detalle/<uuid:pk>/', views.detalle_documento_view, name='detalle_documento'),
    path('editar/<uuid:pk>/', views.editar_documento_view, name='editar_documento'),
    path('eliminar/<uuid:pk>/', views.eliminar_documento_view, name='eliminar_documento'),

    # Descarga y visualización
    path('descargar/<uuid:pk>/', views.descargar_documento, name='descargar_documento'),
    path('preview/<uuid:pk>/', views.preview_documento_view, name='preview_documento'),
    path('ver/<uuid:pk>/', views.ver_documento_view, name='ver_documento'),

    # Gestión de versiones
    path('versiones/<uuid:pk>/', views.versiones_documento_view, name='versiones_documento'),
    path('nueva-version/<uuid:pk>/', views.nueva_version_documento, name='nueva_version_documento'),
    path('comparar-versiones/<uuid:pk>/', views.comparar_versiones_view, name='comparar_versiones'),

    # Categorías y tipos
    path('categorias/', views.categorias_documentos_view, name='categorias_documentos'),
    path('categorias/crear/', views.crear_categoria_documento_view, name='crear_categoria_documento'),
    path('tipos/', views.tipos_documento_view, name='tipos_documento'),
    path('tipos/crear/', views.crear_tipo_documento_view, name='crear_tipo_documento'),

    # Filtrado por categoría
    path('categoria/<int:categoria_id>/', views.documentos_por_categoria_view, name='documentos_por_categoria'),
    path('tipo/<int:tipo_id>/', views.documentos_por_tipo_view, name='documentos_por_tipo'),

    # Documentos por máquina
    path('maquina/<int:maquina_id>/', views.documentos_maquina_view, name='documentos_maquina'),

    # Gestión de acceso
    path('permisos/<uuid:pk>/', views.gestionar_permisos_view, name='gestionar_permisos'),
    path('solicitar-acceso/<uuid:pk>/', views.solicitar_acceso_documento, name='solicitar_acceso'),

    # Comentarios
    path('comentarios/<uuid:pk>/', views.comentarios_documento_view, name='comentarios_documento'),
    path('comentar/<uuid:pk>/', views.agregar_comentario, name='agregar_comentario'),

    # Estadísticas
    path('estadisticas/', views.estadisticas_documentos_view, name='estadisticas_documentos'),
    path('mis-documentos/', views.mis_documentos_view, name='mis_documentos'),
    path('recientes/', views.documentos_recientes_view, name='documentos_recientes'),

    # API endpoints
    path('api/buscar/', views.buscar_documentos_api, name='api_buscar_documentos'),
    path('api/estadisticas/', views.estadisticas_documentos_api, name='api_estadisticas_documentos'),
    path('api/subir/', views.subir_documento_api, name='api_subir_documento'),
    path('api/validar-archivo/', views.validar_archivo_api, name='api_validar_archivo'),

    # Importación masiva
    path('importar/', views.importar_documentos_view, name='importar_documentos'),
    path('indexar/', views.indexar_documentos_view, name='indexar_documentos'),

    # Configuración
    path('configuracion/', views.configuracion_documentos_view, name='configuracion_documentos'),
]