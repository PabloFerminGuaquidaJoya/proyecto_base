from rest_framework import serializers
from django.contrib.auth.models import User

# Import models
from maquinaria.models import Maquina, CategoriaMaquina, Proveedor, AlertaMaquina, HistorialMaquina
from usuarios.models import Usuario, TipoUsuario
from documentos.models import Documento, TipoDocumento, CategoriaDocumento
from reportes.models import Reporte, TipoReporte, MetricasRendimiento


class CategoriaMaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaMaquina
        fields = ['id', 'nombre', 'descripcion', 'icono', 'color', 'activa']


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'nit', 'contacto_nombre', 'contacto_telefono',
            'contacto_email', 'direccion', 'ciudad', 'pais', 'sitio_web',
            'calificacion', 'activo'
        ]


class MaquinaSerializer(serializers.ModelSerializer):
    categoria = CategoriaMaquinaSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    condicion_display = serializers.CharField(source='get_condicion_display', read_only=True)
    necesita_mantenimiento = serializers.BooleanField(read_only=True)

    class Meta:
        model = Maquina
        fields = [
            'id', 'codigo_inventario', 'nombre', 'categoria', 'marca', 'modelo',
            'numero_serie', 'estado', 'estado_display', 'condicion', 'condicion_display',
            'especificaciones_tecnicas', 'capacidad', 'potencia', 'voltaje',
            'dimensiones', 'peso', 'ubicacion', 'centro_formacion',
            'ambiente_formacion', 'proveedor', 'fecha_adquisicion',
            'valor_adquisicion', 'horas_uso_total', 'eficiencia',
            'fecha_ultimo_mantenimiento', 'proximo_mantenimiento',
            'necesita_mantenimiento', 'imagen', 'observaciones', 'created_at'
        ]


class MaquinaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Maquina
        fields = [
            'id', 'codigo_inventario', 'nombre', 'categoria_nombre', 'marca',
            'modelo', 'estado', 'estado_display', 'ubicacion', 'eficiencia'
        ]


class AlertaMaquinaSerializer(serializers.ModelSerializer):
    maquina = MaquinaListSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = AlertaMaquina
        fields = [
            'id', 'maquina', 'tipo', 'tipo_display', 'prioridad', 'prioridad_display',
            'titulo', 'descripcion', 'estado', 'estado_display', 'fecha_creacion',
            'fecha_resolucion', 'notas_resolucion'
        ]


class HistorialMaquinaSerializer(serializers.ModelSerializer):
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)

    class Meta:
        model = HistorialMaquina
        fields = [
            'id', 'tipo_evento', 'tipo_evento_display', 'descripcion',
            'valor_anterior', 'valor_nuevo', 'costo_asociado',
            'fecha_evento', 'usuario_nombre'
        ]


class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['id', 'nombre', 'descripcion', 'permisos', 'activo']


class UsuarioSerializer(serializers.ModelSerializer):
    tipo_usuario = TipoUsuarioSerializer(read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'numero_documento', 'nombres', 'apellidos', 'nombre_completo',
            'email', 'telefono', 'tipo_usuario', 'centro_formacion',
            'especialidad', 'cargo', 'estado', 'estado_display',
            'fecha_registro', 'ultimo_acceso', 'foto_perfil'
        ]


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = [
            'id', 'nombre', 'descripcion', 'extensiones_permitidas',
            'tamaño_maximo_mb', 'icono', 'color', 'activo'
        ]


class CategoriaDocumentoSerializer(serializers.ModelSerializer):
    nivel = serializers.IntegerField(read_only=True)

    class Meta:
        model = CategoriaDocumento
        fields = [
            'id', 'nombre', 'descripcion', 'parent', 'nivel',
            'icono', 'color', 'orden', 'activo'
        ]


class DocumentoSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    categoria = CategoriaDocumentoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    nivel_acceso_display = serializers.CharField(source='get_nivel_acceso_display', read_only=True)
    extension = serializers.CharField(read_only=True)
    tamaño_mb = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Documento
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_documento', 'categoria',
            'archivo', 'tamaño_mb', 'extension', 'version', 'palabras_clave',
            'nivel_acceso', 'nivel_acceso_display', 'estado', 'estado_display',
            'fecha_creacion', 'fecha_modificacion', 'creado_por',
            'total_descargas', 'total_visualizaciones'
        ]


class TipoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReporte
        fields = [
            'id', 'nombre', 'descripcion', 'template_path',
            'parametros_requeridos', 'formato_salida', 'activo'
        ]


class ReporteSerializer(serializers.ModelSerializer):
    tipo_reporte = TipoReporteSerializer(read_only=True)
    usuario_solicitante = UsuarioSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    formato_display = serializers.CharField(source='get_formato_display', read_only=True)

    class Meta:
        model = Reporte
        fields = [
            'id', 'tipo_reporte', 'usuario_solicitante', 'titulo', 'descripcion',
            'formato', 'formato_display', 'estado', 'estado_display',
            'fecha_solicitud', 'fecha_completado', 'archivo_resultado',
            'total_registros', 'veces_descargado'
        ]


class MetricasRendimientoSerializer(serializers.ModelSerializer):
    periodo_display = serializers.CharField(source='get_periodo_display', read_only=True)
    porcentaje_disponibilidad = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    tasa_cumplimiento_mantenimiento = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = MetricasRendimiento
        fields = [
            'id', 'fecha', 'periodo', 'periodo_display', 'centro_formacion',
            'total_maquinas', 'maquinas_operativas', 'maquinas_mantenimiento',
            'eficiencia_promedio', 'horas_uso_total', 'costo_mantenimiento_total',
            'porcentaje_disponibilidad', 'tasa_cumplimiento_mantenimiento',
            'alertas_generadas', 'alertas_resueltas', 'fecha_calculo'
        ]


# Serializers para creación y actualización
class MaquinaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        exclude = ['created_at', 'updated_at', 'created_by']


class AlertaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaMaquina
        exclude = ['fecha_creacion', 'fecha_resolucion', 'resuelto_por', 'created_by']


class DocumentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        exclude = [
            'fecha_creacion', 'fecha_modificacion', 'creado_por',
            'modificado_por', 'total_descargas', 'total_visualizaciones',
            'contenido_texto', 'indices_busqueda'
        ]