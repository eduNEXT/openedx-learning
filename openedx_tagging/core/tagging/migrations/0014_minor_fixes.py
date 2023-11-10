# Generated by Django 3.2.22 on 2023-11-08 22:37

from django.db import migrations, models

import openedx_learning.lib.fields


def fix_language_taxonomy(apps, schema_editor):
    """
    Ensure that the language taxonomy has the correct taxonomy_class. Some
    previous versions of this app's migration history allowed it to be created
    without the right taxonomy_class.
    """
    Taxonomy = apps.get_model("oel_tagging", "Taxonomy")
    correct_class = "openedx_tagging.core.tagging.models.system_defined.LanguageTaxonomy"
    lang_taxonomy = Taxonomy.objects.get(pk=-1)
    if lang_taxonomy._taxonomy_class != correct_class:
        lang_taxonomy._taxonomy_class = correct_class
        lang_taxonomy.save(update_fields=["_taxonomy_class"])


class Migration(migrations.Migration):

    dependencies = [
        ('oel_tagging', '0013_tag_parent_blank'),
    ]

    operations = [
        # Allow taxonomy_class to be blank:
        migrations.AlterField(
            model_name='taxonomy',
            name='_taxonomy_class',
            field=models.CharField(blank=True, help_text='Taxonomy subclass used to instantiate this instance; must be a fully-qualified module and class name. If the module/class cannot be imported, an error is logged and the base Taxonomy class is used instead.', max_length=255, null=True),
        ),
        migrations.RunPython(fix_language_taxonomy, None),
    ]
