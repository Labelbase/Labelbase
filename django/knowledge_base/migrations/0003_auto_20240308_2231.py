# Generated by Django 3.2.24 on 2024-03-08 22:31

from django.db import migrations, models
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge_base', '0002_auto_20240308_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exported_data', jsonfield.fields.JSONField(default={})),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='exclude_from_export',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='category',
            name='exclude_from_export',
            field=models.BooleanField(default=False),
        ),
    ]