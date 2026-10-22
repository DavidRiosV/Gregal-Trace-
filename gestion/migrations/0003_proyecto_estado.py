from django.db import migrations, models


def abierto_a_estado(apps, schema_editor):
    Proyecto = apps.get_model('gestion', 'Proyecto')
    Proyecto.objects.filter(abierto=False).update(estado='TER')


def estado_a_abierto(apps, schema_editor):
    Proyecto = apps.get_model('gestion', 'Proyecto')
    Proyecto.objects.filter(estado='TER').update(abierto=False)


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0002_proyecto_creado_por_proyecto_tipo_destino'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='estado',
            field=models.CharField(choices=[('PRO', 'En proceso'), ('TER', 'Terminado')], default='PRO', max_length=3),
        ),
        migrations.RunPython(abierto_a_estado, estado_a_abierto),
        migrations.RemoveField(
            model_name='proyecto',
            name='abierto',
        ),
    ]
