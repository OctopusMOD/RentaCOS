# Generated by Django 5.2.1 on 2025-06-27 02:11

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flota', '0008_vehiculo_proximo_mantenimiento'),
        ('mantenimiento', '0002_trabajorealizado'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenIngreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_orden', models.CharField(blank=True, max_length=10, unique=True)),
                ('fecha_ingreso', models.DateTimeField(default=django.utils.timezone.now)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('tipo_mantenimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mantenimiento.tipomantenimiento')),
                ('vehiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flota.vehiculo')),
            ],
        ),
        migrations.CreateModel(
            name='TrabajoSolicitado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=255)),
                ('orden_ingreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trabajos', to='mantenimiento.ordeningreso')),
            ],
        ),
    ]
