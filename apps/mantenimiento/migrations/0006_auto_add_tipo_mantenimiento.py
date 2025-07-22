from django.db import migrations

def crear_tipos_mantenimiento(apps, schema_editor):
    TipoMantenimiento = apps.get_model('mantenimiento', 'TipoMantenimiento')
    # Preventivo
    TipoMantenimiento.objects.get_or_create(
        nombre="Preventivo",
        defaults={"es_preventivo": True}
    )
    # Correctivo
    TipoMantenimiento.objects.get_or_create(
        nombre="Correctivo",
        defaults={"es_preventivo": False}
    )
    # Equipamiento
    TipoMantenimiento.objects.get_or_create(
        nombre="Equipamiento",
        defaults={"es_preventivo": False}
    )

class Migration(migrations.Migration):

    dependencies = [
        ('mantenimiento', '0005_remove_ordenmantenimiento_diagnostico_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_tipos_mantenimiento),
    ]