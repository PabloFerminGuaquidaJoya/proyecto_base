from django.urls import path
from . import views

app_name = 'sistema'

urlpatterns = [
    # Status endpoints
    path('status/', views.status_check, name='status_check'),
    path('health/', views.health_check, name='health_check'),
    path('version/', views.version_info, name='version_info'),
    path('database/', views.database_status, name='database_status'),

    # Backup endpoints
    path('backups/', views.gestionar_backups, name='gestionar_backups'),
    path('backups/crear/', views.crear_backup, name='crear_backup'),
    path('backups/crear-rapido/', views.crear_backup_rapido, name='crear_backup_rapido'),
    path('backups/<uuid:backup_id>/restaurar/', views.restaurar_backup, name='restaurar_backup'),
    path('backups/<uuid:backup_id>/descargar/', views.descargar_backup, name='descargar_backup'),
    path('backups/<uuid:backup_id>/eliminar/', views.eliminar_backup, name='eliminar_backup'),
    path('backups/<uuid:backup_id>/detalle/', views.detalle_backup, name='detalle_backup'),

    # Centro Administrativo
    path('centro-administrativo/', views.centro_administrativo_view, name='centro_administrativo'),
    path('centros/crear/', views.admin_crear_centro, name='admin_crear_centro'),
    path('centros/<int:pk>/editar/', views.admin_editar_centro, name='admin_editar_centro'),
    path('centros/<int:pk>/eliminar/', views.admin_eliminar_centro, name='admin_eliminar_centro'),
    path('ambientes/crear/', views.admin_crear_ambiente, name='admin_crear_ambiente'),
    path('ambientes/<int:pk>/editar/', views.admin_editar_ambiente, name='admin_editar_ambiente'),
    path('ambientes/<int:pk>/eliminar/', views.admin_eliminar_ambiente, name='admin_eliminar_ambiente'),
    # Fichas
    path('fichas/crear/', views.admin_crear_ficha, name='admin_crear_ficha'),
    path('fichas/<int:pk>/editar/', views.admin_editar_ficha, name='admin_editar_ficha'),
    path('fichas/<int:pk>/eliminar/', views.admin_eliminar_ficha, name='admin_eliminar_ficha'),
]
