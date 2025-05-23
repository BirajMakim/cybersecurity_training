# Generated by Django 5.2 on 2025-05-07 10:13

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0007_trainingmodule_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningpath',
            name='overview',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Overview or structure of the learning path (supports rich text)'),
        ),
    ]
