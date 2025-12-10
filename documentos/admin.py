from django.contrib import admin
from .models import TipoDocumento, CategoriaDocumento, Documento

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tamaño_maximo_mb', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'parent', 'orden', 'activo']
    list_filter = ['activo', 'parent']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_documento', 'categoria', 'estado', 'nivel_acceso', 'creado_por', 'fecha_creacion']
    list_filter = ['estado', 'nivel_acceso', 'tipo_documento', 'categoria', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'contenido_texto']
    readonly_fields = ['id', 'fecha_creacion', 'fecha_modificacion', 'tamaño_archivo', 'checksum']
    ordering = ['-fecha_creacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo_documento', 'categoria')
        }),
        ('Archivo', {
            'fields': ('archivo', 'tamaño_archivo', 'checksum')
        }),
        ('Metadatos', {
            'fields': ('version', 'palabras_clave', 'autor_original')
        }),
        ('Control de Acceso', {
            'fields': ('nivel_acceso', 'usuarios_acceso')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_publicacion', 'fecha_vencimiento')
        }),
        ('Relaciones', {
            'fields': ('creado_por', 'modificado_por', 'maquina_relacionada')
        }),
        ('Estadísticas', {
            'fields': ('total_descargas', 'total_visualizaciones', 'ultima_descarga')
        }),
        ('Sistema', {
            'fields': ('id', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
