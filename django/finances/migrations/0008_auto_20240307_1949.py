# Generated by Django 3.2.24 on 2024-03-07 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finances', '0007_outputstat_last_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='outputstat',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='outputstat',
            unique_together={('user', 'type_ref_hash')},
        ),
    ]
