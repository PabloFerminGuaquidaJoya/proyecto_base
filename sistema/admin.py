from django.contrib import admin
from .models import Configuracion, Notificacion, LogActividad, BackupDatabase

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'tipo_valor', 'categoria', 'publico', 'modificable']
    list_filter = ['categoria', 'tipo_valor', 'publico', 'modificable']
    search_fields = ['clave', 'descripcion']
    ordering = ['categoria', 'clave']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'estado', 'fecha_creacion']
    list_filter = ['tipo', 'estado', 'enviado_por_sistema']
    search_fields = ['titulo', 'mensaje']
    ordering = ['-fecha_creacion']
    readonly_fields = ['id', 'fecha_creacion']

@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'usuario', 'modulo', 'nivel', 'accion']
    list_filter = ['nivel', 'modulo', 'timestamp']
    search_fields = ['accion', 'descripcion', 'usuario__nombre_completo']
    ordering = ['-timestamp']
    readonly_fields = ['id', 'timestamp']

@admin.register(BackupDatabase)
class BackupDatabaseAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'tipo', 'creado_por', 'fecha_creacion']
    list_filter = ['estado', 'tipo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['-fecha_creacion']
    readonly_fields = ['id', 'fecha_creacion', 'total_tablas', 'total_registros']
