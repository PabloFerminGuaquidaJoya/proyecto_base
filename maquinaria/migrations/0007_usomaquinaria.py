from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maquinaria', '0006_objetomaquinaria'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsoMaquinaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ficha', models.CharField(max_length=50, verbose_name='Ficha')),
                ('fecha', models.DateField(verbose_name='Fecha')),
                ('hora_inicio', models.TimeField(verbose_name='Hora Inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora Fin')),
                ('horas_uso', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Horas de Uso (sesión)')),
                ('horas_totales_maquina', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Horas Totales de la Máquina')),
                ('descripcion_actividad', models.TextField(verbose_name='Descripción de la Actividad')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('instructor_encargado', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='usos_maquinaria_instructor',
                    to='usuarios.usuario',
                    verbose_name='Instructor Encargado',
                )),
                ('maquina', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registros_uso',
                    to='maquinaria.maquina',
                    verbose_name='Máquina',
                )),
                ('registrado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='usos_maquinaria_registrados',
                    to='usuarios.usuario',
                    verbose_name='Registrado Por',
                )),
            ],
            options={
                'verbose_name': 'Uso de Maquinaria',
                'verbose_name_plural': 'Usos de Maquinaria',
                'ordering': ['-fecha', '-hora_inicio'],
                'indexes': [
                    models.Index(fields=['maquina', '-fecha'], name='maq_uso_maquina_fecha_idx'),
                    models.Index(fields=['ficha'], name='maq_uso_ficha_idx'),
                ],
            },
        ),
    ]
