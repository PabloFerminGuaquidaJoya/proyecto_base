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
]
