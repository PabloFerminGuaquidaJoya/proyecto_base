from django.core.management.base import BaseCommand
from documentos.models import TipoDocumento, CategoriaDocumento


class Command(BaseCommand):
    help = 'Pobla la base de datos con tipos y categorías de documentos'

    def handle(self, *args, **kwargs):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("POBLANDO BASE DE DATOS - MÓDULO DOCUMENTOS")
        self.stdout.write("=" * 60)

        self.poblar_tipos_documento()
        self.poblar_categorias_documento()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("PROCESO COMPLETADO")
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nTipos de documento: {TipoDocumento.objects.count()}")
        self.stdout.write(f"Categorías de documento: {CategoriaDocumento.objects.count()}")
        self.stdout.write("=" * 60 + "\n")

    def poblar_tipos_documento(self):
        """Crear tipos de documento predefinidos"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("CREANDO TIPOS DE DOCUMENTO")
        self.stdout.write("=" * 60)

        tipos = [
            {
                'nombre': 'Manual de Operación',
                'descripcion': 'Manuales de operación y uso de maquinaria',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
                'tamaño_maximo_mb': 50,
                'icono': 'bi-book',
                'color': '#007bff',
            },
            {
                'nombre': 'Manual de Mantenimiento',
                'descripcion': 'Manuales de mantenimiento preventivo y correctivo',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
                'tamaño_maximo_mb': 50,
                'icono': 'bi-tools',
                'color': '#28a745',
            },
            {
                'nombre': 'Ficha Técnica',
                'descripcion': 'Fichas técnicas y especificaciones',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'],
                'tamaño_maximo_mb': 25,
                'icono': 'bi-file-earmark-text',
                'color': '#17a2b8',
            },
            {
                'nombre': 'Planos',
                'descripcion': 'Planos técnicos y diagramas',
                'extensiones_permitidas': ['.pdf', '.dwg', '.dxf'],
                'tamaño_maximo_mb': 100,
                'icono': 'bi-diagram-3',
                'color': '#ffc107',
            },
            {
                'nombre': 'Certificado',
                'descripcion': 'Certificados de calibración, calidad, etc.',
                'extensiones_permitidas': ['.pdf'],
                'tamaño_maximo_mb': 10,
                'icono': 'bi-award',
                'color': '#fd7e14',
            },
            {
                'nombre': 'Procedimiento',
                'descripcion': 'Procedimientos operativos estándar',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
                'tamaño_maximo_mb': 25,
                'icono': 'bi-list-check',
                'color': '#6610f2',
            },
            {
                'nombre': 'Reporte',
                'descripcion': 'Reportes de inspección, auditoría, etc.',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'],
                'tamaño_maximo_mb': 30,
                'icono': 'bi-file-earmark-bar-graph',
                'color': '#e83e8c',
            },
            {
                'nombre': 'Otro',
                'descripcion': 'Otros documentos',
                'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.ppt', '.pptx'],
                'tamaño_maximo_mb': 50,
                'icono': 'bi-file-earmark',
                'color': '#6c757d',
            },
        ]

        created_count = 0
        updated_count = 0

        for tipo_data in tipos:
            tipo, created = TipoDocumento.objects.update_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [CREADO] {tipo.nombre}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"  [ACTUALIZADO] {tipo.nombre}"))
                updated_count += 1

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(f"Tipos creados: {created_count}")
        self.stdout.write(f"Tipos actualizados: {updated_count}")
        self.stdout.write(f"Total tipos: {TipoDocumento.objects.count()}")
        self.stdout.write("=" * 60)

    def poblar_categorias_documento(self):
        """Crear categorías de documento predefinidas"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("CREANDO CATEGORÍAS DE DOCUMENTO")
        self.stdout.write("=" * 60)

        categorias = [
            {
                'nombre': 'Maquinaria',
                'descripcion': 'Documentos relacionados con maquinaria',
                'icono': 'bi-gear-fill',
                'color': '#007bff',
                'orden': 1,
            },
            {
                'nombre': 'Seguridad',
                'descripcion': 'Documentos de seguridad industrial',
                'icono': 'bi-shield-check',
                'color': '#28a745',
                'orden': 2,
            },
            {
                'nombre': 'Calidad',
                'descripcion': 'Documentos de control de calidad',
                'icono': 'bi-clipboard-check',
                'color': '#17a2b8',
                'orden': 3,
            },
            {
                'nombre': 'Mantenimiento',
                'descripcion': 'Documentos de mantenimiento',
                'icono': 'bi-tools',
                'color': '#ffc107',
                'orden': 4,
            },
            {
                'nombre': 'Operación',
                'descripcion': 'Documentos de operación',
                'icono': 'bi-play-circle',
                'color': '#fd7e14',
                'orden': 5,
            },
            {
                'nombre': 'Técnica',
                'descripcion': 'Documentos técnicos generales',
                'icono': 'bi-file-earmark-code',
                'color': '#6610f2',
                'orden': 6,
            },
            {
                'nombre': 'Administrativa',
                'descripcion': 'Documentos administrativos',
                'icono': 'bi-briefcase',
                'color': '#e83e8c',
                'orden': 7,
            },
            {
                'nombre': 'General',
                'descripcion': 'Documentos generales',
                'icono': 'bi-folder',
                'color': '#6c757d',
                'orden': 8,
            },
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categorias:
            categoria, created = CategoriaDocumento.objects.update_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [CREADO] {categoria.nombre}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"  [ACTUALIZADO] {categoria.nombre}"))
                updated_count += 1

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(f"Categorías creadas: {created_count}")
        self.stdout.write(f"Categorías actualizadas: {updated_count}")
        self.stdout.write(f"Total categorías: {CategoriaDocumento.objects.count()}")
        self.stdout.write("=" * 60)
