# Generated by Django 5.0.6 on 2025-03-16 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryimage',
            old_name='product',
            new_name='category',
        ),
    ]
