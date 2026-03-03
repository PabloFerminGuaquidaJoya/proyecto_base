from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_add_fotos_pieza_empaque'),
        ('maquinaria', '0006_objetomaquinaria'),
    ]

    operations = [
        migrations.AddField(
            model_name='piezainventario',
            name='fabricante',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='color',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='maquina',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='piezas_inventario',
                to='maquinaria.maquina',
            ),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='fecha_compra',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='fecha_uso',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='fecha_cambio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_frontal',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_lateral_derecha',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_lateral_izquierda',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_trasera',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_superior',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
        migrations.AddField(
            model_name='piezainventario',
            name='foto_inferior',
            field=models.ImageField(blank=True, null=True, upload_to='inventario/angulos/'),
        ),
    ]
