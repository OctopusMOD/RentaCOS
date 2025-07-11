# Generated by Django 5.2.1 on 2025-06-12 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flota', '0002_marca_alter_vehiculo_options_remove_vehiculo_año_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=64, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='tenencia',
            field=models.CharField(choices=[('PROPIO', 'Propio'), ('SUBARRENDADO', 'Subarrendado'), ('LEASING', 'Leasing'), ('CLIENTE', 'Cliente'), ('OTRO', 'Otro')], default='PROPIO', max_length=16),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='traccion',
            field=models.CharField(choices=[('4x2', '4x2'), ('4x4', '4x4'), ('AWD', 'AWD'), ('OTRO', 'Otro')], default='4x2', max_length=16),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='vin',
            field=models.CharField(default='VINPRUEBA123', max_length=32, unique=True, verbose_name='VIN/Chasis'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='grupo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehiculos', to='flota.grupovehiculo'),
        ),
    ]
