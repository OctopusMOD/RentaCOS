# Generated by Django 5.2.1 on 2025-07-06 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alquiler', '0006_alter_contrato_options_contrato_vehiculo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='descuento_porcentaje',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Porcentaje de descuento aplicado al subtotal (0-100%).', max_digits=5, verbose_name='Descuento (%)'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha fin arriendo'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha inicio arriendo'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='monto_total',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total final a pagar por el contrato, calculado automáticamente.', max_digits=12, null=True, verbose_name='Monto total del contrato'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='tarifa_diaria',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Tarifa diaria base del arriendo (puede venir del grupo o del vehículo, editable por el usuario).', max_digits=10, null=True, verbose_name='Tarifa diaria'),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='estado',
            field=models.CharField(choices=[('POR_FIRMAR', 'Por firmar'), ('ACTIVO', 'Activo'), ('FINALIZADO', 'Finalizado'), ('CANCELADO', 'Cancelado')], default='POR_FIRMAR', max_length=20),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='fecha_firma',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de firma'),
        ),
    ]
