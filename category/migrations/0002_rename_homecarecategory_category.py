# Generated by Django 5.0 on 2024-10-22 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HomeCareCategory',
            new_name='Category',
        ),
    ]