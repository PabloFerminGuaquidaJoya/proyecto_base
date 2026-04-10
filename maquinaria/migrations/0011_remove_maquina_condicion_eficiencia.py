from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maquinaria', '0010_alter_maquina_peso'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maquina',
            name='condicion',
        ),
        migrations.RemoveField(
            model_name='maquina',
            name='eficiencia',
        ),
    ]
