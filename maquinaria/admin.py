from django.contrib import admin
from .models import CategoriaMaquina, Proveedor, Maquina, HistorialMaquina, AlertaMaquina, MaquinaEliminada

@admin.register(CategoriaMaquina)
class CategoriaMaquinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activa', 'created_at')
    list_filter = ('activa', 'created_at')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activa',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto_telefono', 'contacto_email', 'ciudad', 'activo', 'created_at')
    list_filter = ('activo', 'ciudad', 'created_at')
    search_fields = ('nombre', 'contacto_email', 'contacto_telefono', 'contacto_nombre')
    list_editable = ('activo',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nit', 'contacto_nombre', 'activo')
        }),
        ('Contacto', {
            'fields': ('contacto_telefono', 'contacto_email', 'direccion', 'ciudad', 'pais')
        }),
        ('Información Adicional', {
            'fields': ('sitio_web', 'calificacion'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('codigo_inventario', 'nombre', 'categoria', 'marca', 'estado', 'condicion', 'fecha_adquisicion')
    list_filter = ('estado', 'condicion', 'categoria', 'marca', 'fecha_adquisicion')
    search_fields = ('codigo_inventario', 'nombre', 'marca', 'modelo', 'numero_serie')
    list_editable = ('estado', 'condicion')
    date_hierarchy = 'fecha_adquisicion'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_inventario', 'nombre', 'categoria', 'marca', 'modelo', 'numero_serie')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('potencia', 'peso', 'capacidad', 'voltaje', 'dimensiones', 'especificaciones_tecnicas')
        }),
        ('Ubicación y Estado', {
            'fields': ('centro_formacion', 'ubicacion', 'estado', 'condicion')
        }),
        ('Información Comercial', {
            'fields': ('proveedor', 'valor_adquisicion', 'fecha_adquisicion', 'eficiencia')
        }),
        ('Uso y Mantenimiento', {
            'fields': ('horas_uso_total', 'proximo_mantenimiento')
        }),
        ('Archivos', {
            'fields': ('imagen', 'manual_pdf'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(HistorialMaquina)
class HistorialMaquinaAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'tipo_evento', 'fecha_evento', 'usuario', 'descripcion_corta')
    list_filter = ('tipo_evento', 'fecha_evento', 'maquina__categoria')
    search_fields = ('maquina__codigo_inventario', 'maquina__nombre', 'descripcion')
    date_hierarchy = 'fecha_evento'
    readonly_fields = ('fecha_evento',)

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

@admin.register(AlertaMaquina)
class AlertaMaquinaAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'tipo', 'prioridad', 'estado', 'fecha_creacion', 'fecha_resolucion')
    list_filter = ('tipo', 'prioridad', 'estado', 'fecha_creacion')
    search_fields = ('maquina__codigo_inventario', 'maquina__nombre', 'mensaje')
    list_editable = ('estado',)
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)

@admin.register(MaquinaEliminada)
class MaquinaEliminadaAdmin(admin.ModelAdmin):
    list_display = ('codigo_inventario', 'nombre', 'categoria_nombre', 'fecha_eliminacion', 'eliminado_por', 'total_mantenimientos', 'total_alertas')
    list_filter = ('fecha_eliminacion', 'categoria_nombre', 'estado_final', 'condicion_final')
    search_fields = ('codigo_inventario', 'nombre', 'marca', 'modelo', 'numero_serie', 'motivo_eliminacion')
    date_hierarchy = 'fecha_eliminacion'
    readonly_fields = (
        'codigo_inventario', 'nombre', 'marca', 'modelo', 'numero_serie', 'categoria_nombre',
        'estado_final', 'condicion_final', 'ubicacion', 'centro_formacion',
        'horas_uso_total', 'eficiencia_final', 'datos_completos_maquina',
        'historial_completo', 'alertas_asociadas', 'mantenimientos_realizados',
        'fecha_eliminacion', 'eliminado_por', 'total_mantenimientos',
        'total_reparaciones', 'total_alertas', 'costo_total_mantenimiento', 'dias_operacion'
    )

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_inventario', 'nombre', 'marca', 'modelo', 'numero_serie', 'categoria_nombre')
        }),
        ('Estado Final', {
            'fields': ('estado_final', 'condicion_final', 'ubicacion', 'centro_formacion')
        }),
        ('Datos de Uso', {
            'fields': ('horas_uso_total', 'eficiencia_final', 'dias_operacion')
        }),
        ('Estadísticas', {
            'fields': ('total_mantenimientos', 'total_reparaciones', 'total_alertas', 'costo_total_mantenimiento')
        }),
        ('Eliminación', {
            'fields': ('fecha_eliminacion', 'eliminado_por', 'motivo_eliminacion', 'observaciones_finales')
        }),
        ('Datos Completos (JSON)', {
            'fields': ('datos_completos_maquina', 'historial_completo', 'alertas_asociadas', 'mantenimientos_realizados'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        # No permitir agregar registros manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo permitir eliminar con permisos especiales
        return request.user.is_superuser

