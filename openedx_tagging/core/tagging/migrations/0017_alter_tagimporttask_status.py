# Generated by Django 4.2.11 on 2024-04-05 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oel_tagging', '0016_object_tag_export_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagimporttask',
            name='status',
            field=models.CharField(choices=[('loading_data', 'Loading Data'), ('planning', 'Planning'), ('executing', 'Executing'), ('success', 'Success'), ('error', 'Error')], help_text='Task status', max_length=20),
        ),
    ]
