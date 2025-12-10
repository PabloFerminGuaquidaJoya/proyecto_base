from django.contrib import admin
from .models import Usuario, TipoUsuario, SesionUsuario, TokenRecuperacionPassword

@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo', 'created_at')
    list_filter = ('activo', 'created_at')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombre_completo', 'email', 'tipo_usuario', 'estado', 'fecha_registro')
    list_filter = ('estado', 'tipo_usuario', 'fecha_registro', 'centro_formacion')
    search_fields = ('numero_documento', 'nombres', 'apellidos', 'email', 'telefono')
    list_editable = ('estado',)
    readonly_fields = ('fecha_registro', 'ultimo_acceso', 'created_at', 'updated_at')

    fieldsets = (
        ('Información Personal', {
            'fields': ('tipo_documento', 'numero_documento', 'nombres', 'apellidos', 'email', 'telefono', 'foto_perfil')
        }),
        ('Información Institucional', {
            'fields': ('tipo_usuario', 'centro_formacion', 'especialidad', 'cargo')
        }),
        ('Estado y Configuración', {
            'fields': ('estado', 'notificaciones_email', 'tema_oscuro', 'idioma')
        }),
        ('Metadatos', {
            'fields': ('fecha_registro', 'fecha_aprobacion', 'ultimo_acceso', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )

@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_inicio', 'fecha_fin', 'activa', 'ip_address')
    list_filter = ('activa', 'fecha_inicio')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'ip_address')
    readonly_fields = ('fecha_inicio',)

@admin.register(TokenRecuperacionPassword)
class TokenRecuperacionPasswordAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'fecha_expiracion', 'usado', 'ip_solicitud')
    list_filter = ('usado', 'fecha_creacion')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'usuario__email', 'token')
    readonly_fields = ('token', 'fecha_creacion', 'fecha_expiracion', 'ip_solicitud')

    def has_add_permission(self, request):
        # No permitir crear tokens manualmente desde el admin
        return False
