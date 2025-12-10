# Ejecuta este codigo en el shell de Django: python manage.py shell
# Luego copia y pega este contenido

from documentos.models import TipoDocumento, CategoriaDocumento

# Crear Tipos de Documento
tipos = [
    {'nombre': 'Manual de Operacion', 'descripcion': 'Manuales de operacion y uso de maquinaria', 'extensiones_permitidas': ['.pdf', '.doc', '.docx'], 'tamaño_maximo_mb': 50, 'icono': 'bi-book', 'color': '#007bff'},
    {'nombre': 'Manual de Mantenimiento', 'descripcion': 'Manuales de mantenimiento preventivo y correctivo', 'extensiones_permitidas': ['.pdf', '.doc', '.docx'], 'tamaño_maximo_mb': 50, 'icono': 'bi-tools', 'color': '#28a745'},
    {'nombre': 'Ficha Tecnica', 'descripcion': 'Fichas tecnicas y especificaciones', 'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'], 'tamaño_maximo_mb': 25, 'icono': 'bi-file-earmark-text', 'color': '#17a2b8'},
    {'nombre': 'Planos', 'descripcion': 'Planos tecnicos y diagramas', 'extensiones_permitidas': ['.pdf', '.dwg', '.dxf'], 'tamaño_maximo_mb': 100, 'icono': 'bi-diagram-3', 'color': '#ffc107'},
    {'nombre': 'Certificado', 'descripcion': 'Certificados de calibracion, calidad, etc.', 'extensiones_permitidas': ['.pdf'], 'tamaño_maximo_mb': 10, 'icono': 'bi-award', 'color': '#fd7e14'},
    {'nombre': 'Procedimiento', 'descripcion': 'Procedimientos operativos estandar', 'extensiones_permitidas': ['.pdf', '.doc', '.docx'], 'tamaño_maximo_mb': 25, 'icono': 'bi-list-check', 'color': '#6610f2'},
    {'nombre': 'Reporte', 'descripcion': 'Reportes de inspeccion, auditoria, etc.', 'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'], 'tamaño_maximo_mb': 30, 'icono': 'bi-file-earmark-bar-graph', 'color': '#e83e8c'},
    {'nombre': 'Otro', 'descripcion': 'Otros documentos', 'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.ppt', '.pptx'], 'tamaño_maximo_mb': 50, 'icono': 'bi-file-earmark', 'color': '#6c757d'},
]

for tipo_data in tipos:
    tipo, created = TipoDocumento.objects.update_or_create(nombre=tipo_data['nombre'], defaults=tipo_data)
    print(f"{'[CREADO]' if created else '[ACTUALIZADO]'} {tipo.nombre}")

print(f"\nTotal tipos: {TipoDocumento.objects.count()}")

# Crear Categorias de Documento
categorias = [
    {'nombre': 'Maquinaria', 'descripcion': 'Documentos relacionados con maquinaria', 'icono': 'bi-gear-fill', 'color': '#007bff', 'orden': 1},
    {'nombre': 'Seguridad', 'descripcion': 'Documentos de seguridad industrial', 'icono': 'bi-shield-check', 'color': '#28a745', 'orden': 2},
    {'nombre': 'Calidad', 'descripcion': 'Documentos de control de calidad', 'icono': 'bi-clipboard-check', 'color': '#17a2b8', 'orden': 3},
    {'nombre': 'Mantenimiento', 'descripcion': 'Documentos de mantenimiento', 'icono': 'bi-tools', 'color': '#ffc107', 'orden': 4},
    {'nombre': 'Operacion', 'descripcion': 'Documentos de operacion', 'icono': 'bi-play-circle', 'color': '#fd7e14', 'orden': 5},
    {'nombre': 'Tecnica', 'descripcion': 'Documentos tecnicos generales', 'icono': 'bi-file-earmark-code', 'color': '#6610f2', 'orden': 6},
    {'nombre': 'Administrativa', 'descripcion': 'Documentos administrativos', 'icono': 'bi-briefcase', 'color': '#e83e8c', 'orden': 7},
    {'nombre': 'General', 'descripcion': 'Documentos generales', 'icono': 'bi-folder', 'color': '#6c757d', 'orden': 8},
]

for cat_data in categorias:
    categoria, created = CategoriaDocumento.objects.update_or_create(nombre=cat_data['nombre'], defaults=cat_data)
    print(f"{'[CREADO]' if created else '[ACTUALIZADO]'} {categoria.nombre}")

print(f"\nTotal categorias: {CategoriaDocumento.objects.count()}")
print("\nProceso completado!")
