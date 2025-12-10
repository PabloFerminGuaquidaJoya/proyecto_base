from django.contrib import admin
from .models import TipoReporte, Reporte, MetricasRendimiento

@admin.register(TipoReporte)
class TipoReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo', 'created_at')
    list_filter = ('activo', 'created_at')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_reporte', 'usuario_solicitante', 'estado', 'formato', 'fecha_solicitud')
    list_filter = ('estado', 'formato', 'tipo_reporte', 'fecha_solicitud')
    search_fields = ('titulo', 'descripcion', 'usuario_solicitante__nombre_completo')
    readonly_fields = ('id', 'fecha_solicitud', 'fecha_inicio_procesamiento', 'fecha_completado', 'tiempo_procesamiento')
    date_hierarchy = 'fecha_solicitud'

@admin.register(MetricasRendimiento)
class MetricasRendimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'periodo', 'centro_formacion', 'categoria_maquina', 'total_maquinas', 'eficiencia_promedio')
    list_filter = ('periodo', 'centro_formacion', 'categoria_maquina', 'fecha')
    search_fields = ('centro_formacion',)
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha_calculo', 'porcentaje_disponibilidad', 'tasa_cumplimiento_mantenimiento')
