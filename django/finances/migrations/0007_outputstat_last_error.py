# Generated by Django 3.2.24 on 2024-03-07 15:24

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0006_alter_outputstat_type_ref_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='outputstat',
            name='last_error',
            field=jsonfield.fields.JSONField(default=None, null=True),
        ),
    ]