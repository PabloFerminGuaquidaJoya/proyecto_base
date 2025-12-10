"""
Script para crear tipos de reporte en la base de datos
Ejecutar con: python crear_tipos_reporte_script.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from reportes.models import TipoReporte

def crear_tipos_reporte():
    """Crea los tipos de reporte predeterminados"""
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

    print("Iniciando creación de tipos de reporte...")
    print("-" * 50)

    for tipo_data in tipos_reporte:
        try:
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
                print(f'[OK] Tipo de reporte creado: {tipo.nombre}')
            else:
                # Actualizar si ya existe
                tipo.descripcion = tipo_data['descripcion']
                tipo.parametros_requeridos = tipo_data['parametros_requeridos']
                tipo.formato_salida = tipo_data['formato_salida']
                tipo.activo = True
                tipo.save()
                updated_count += 1
                print(f'[UPDATE] Tipo de reporte actualizado: {tipo.nombre}')
        except Exception as e:
            print(f'[ERROR] Error al crear/actualizar {tipo_data["nombre"]}: {str(e)}')

    print("-" * 50)
    print(f'[COMPLETADO] Proceso completado: {created_count} creados, {updated_count} actualizados')

    # Mostrar todos los tipos de reporte activos
    print("\nTipos de reporte activos en la base de datos:")
    print("-" * 50)
    tipos_activos = TipoReporte.objects.filter(activo=True)
    for tipo in tipos_activos:
        print(f"  - {tipo.nombre} (ID: {tipo.id})")
    print(f"\nTotal: {tipos_activos.count()} tipos de reporte activos")

if __name__ == '__main__':
    crear_tipos_reporte()
