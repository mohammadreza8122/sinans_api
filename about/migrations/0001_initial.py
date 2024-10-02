# Generated by Django 5.0 on 2024-09-17 20:13

import ckeditor_uploader.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='About',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان/سمت')),
                ('text', models.TextField(blank=True, null=True, verbose_name='توضیحات تکمیلی')),
            ],
            options={
                'verbose_name': 'درباره',
                'verbose_name_plural': 'درباره سینانس',
            },
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='نام')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان/سمت')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='تصویر')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='ایمیل')),
                ('instagram', models.CharField(blank=True, max_length=255, null=True, verbose_name='اینستاگرام')),
                ('whatsapp', models.CharField(blank=True, max_length=255, null=True, verbose_name='واتساپ')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='شماره تماس')),
            ],
            options={
                'verbose_name': 'پشتیبانی',
                'verbose_name_plural': 'پشتیبانی',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='نام')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان/سمت')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='تصویر')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='ایمیل')),
                ('instagram', models.CharField(blank=True, max_length=255, null=True, verbose_name='اینستاگرام')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='شماره تماس')),
            ],
            options={
                'verbose_name': 'تیم',
                'verbose_name_plural': 'تیم',
            },
        ),
        migrations.CreateModel(
            name='AboutSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='متن')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='تصویر')),
                ('about', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sections', to='about.about', verbose_name='درباره')),
            ],
            options={
                'verbose_name': 'بخش',
                'verbose_name_plural': 'بخش',
            },
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveIntegerField(default=1, verbose_name='ترتیب')),
                ('title', models.CharField(max_length=255, verbose_name='عنوان')),
                ('about', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statistics', to='about.about', verbose_name='درباره')),
            ],
            options={
                'verbose_name': 'آمار',
                'verbose_name_plural': 'آمارها',
                'ordering': ('row',),
            },
        ),
    ]