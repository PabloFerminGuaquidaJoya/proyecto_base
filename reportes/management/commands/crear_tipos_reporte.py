from django.core.management.base import BaseCommand
from reportes.models import TipoReporte


class Command(BaseCommand):
    help = 'Crea los tipos de reporte predeterminados'

    def handle(self, *args, **kwargs):
        tipos_reporte = [
            {
                'nombre': 'Estado de Maquinaria',
                'descripcion': 'Reporte completo del estado actual de toda la maquinaria, incluyendo distribución por categorías, máquinas operativas vs no operativas, y alertas activas.',
                'parametros_requeridos': ['fecha_inicio', 'fecha_fin'],
                'formato_salida': ['pdf', 'excel', 'csv'],
            },
            {
                'nombre': 'Mantenimiento',
                'descripcion': 'Cronograma de mantenimientos realizados y programados, costos asociados, análisis de frecuencia de fallas y recomendaciones predictivas.',
                'parametros_requeridos': ['fecha_inicio', 'fecha_fin'],
                'formato_salida': ['pdf', 'excel'],
            },
            {
                'nombre': 'Costos Operativos',
                'descripcion': 'Análisis detallado de costos operativos por máquina, gastos de combustible y lubricantes, inversión en mantenimiento, ROI y proyecciones.',
                'parametros_requeridos': ['fecha_inicio', 'fecha_fin'],
                'formato_salida': ['pdf', 'excel', 'csv'],
            },
            {
                'nombre': 'Eficiencia',
                'descripcion': 'Métricas de utilización por máquina, tiempo de operación vs inactividad, indicadores de rendimiento (KPIs), y comparativas de eficiencia.',
                'parametros_requeridos': ['fecha_inicio', 'fecha_fin'],
                'formato_salida': ['pdf', 'excel'],
            },
        ]

        created_count = 0
        updated_count = 0

        for tipo_data in tipos_reporte:
            tipo, created = TipoReporte.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'parametros_requeridos': tipo_data['parametros_requeridos'],
                    'formato_salida': tipo_data['formato_salida'],
                    'activo': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Tipo de reporte creado: {tipo.nombre}')
                )
            else:
                # Actualizar si ya existe
                tipo.descripcion = tipo_data['descripcion']
                tipo.parametros_requeridos = tipo_data['parametros_requeridos']
                tipo.formato_salida = tipo_data['formato_salida']
                tipo.activo = True
                tipo.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Tipo de reporte actualizado: {tipo.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_count} creados, {updated_count} actualizados'
            )
        )
