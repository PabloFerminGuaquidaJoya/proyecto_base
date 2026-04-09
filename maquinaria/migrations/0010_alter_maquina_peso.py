from django.db import migrations, models


def limpiar_peso_no_numerico(apps, schema_editor):
    """Nullifica valores de peso que no sean numéricos antes de cambiar el tipo."""
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        # Nullificar valores vacíos o que no sean números válidos
        cursor.execute("""
            UPDATE maquinaria_maquina
            SET peso = NULL
            WHERE peso = ''
               OR peso IS NOT NULL
               AND peso REGEXP '[^0-9.]'
        """)


class Migration(migrations.Migration):

    atomic = False  # MySQL no soporta DDL transaccional

    dependencies = [
        ('maquinaria', '0009_rename_maq_uso_maquina_fecha_idx_maquinaria__maquina_633d0a_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(limpiar_peso_no_numerico, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='maquina',
            name='peso',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=8,
                null=True,
                verbose_name='Peso (kg)',
            ),
        ),
    ]
