from django.contrib import admin
from .models import Usuario, TipoUsuario, SesionUsuario, TokenRecuperacionPassword, ReconocimientoFacial, IntentoReconocimientoFacial

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


@admin.register(ReconocimientoFacial)
class ReconocimientoFacialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'activo', 'fecha_registro', 'fecha_actualizacion', 'confianza_registro', 'ip_registro')
    list_filter = ('activo', 'fecha_registro', 'fecha_actualizacion')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'usuario__numero_documento', 'ip_registro')
    list_editable = ('activo',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion', 'ip_registro', 'user_agent_registro')

    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'activo')
        }),
        ('Datos de Registro', {
            'fields': ('embedding', 'confianza_registro', 'fecha_registro', 'fecha_actualizacion')
        }),
        ('Auditoría', {
            'fields': ('ip_registro', 'user_agent_registro'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        # No permitir crear registros manualmente desde el admin
        return False


@admin.register(IntentoReconocimientoFacial)
class IntentoReconocimientoFacialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_intento', 'resultado', 'similitud', 'fecha_intento', 'ip_address')
    list_filter = ('tipo_intento', 'resultado', 'fecha_intento')
    search_fields = ('usuario__nombres', 'usuario__apellidos', 'usuario__numero_documento', 'ip_address', 'mensaje_error')
    readonly_fields = ('usuario', 'tipo_intento', 'resultado', 'similitud', 'mensaje_error', 'fecha_intento', 'ip_address', 'user_agent')
    ordering = ('-fecha_intento',)

    fieldsets = (
        ('Información del Intento', {
            'fields': ('usuario', 'tipo_intento', 'resultado', 'similitud', 'fecha_intento')
        }),
        ('Detalles del Error', {
            'fields': ('mensaje_error',)
        }),
        ('Auditoría', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        # No permitir crear registros manualmente desde el admin
        return False

    def has_change_permission(self, request, obj=None):
        # Solo lectura en el admin
        return False
