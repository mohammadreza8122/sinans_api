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
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='عنوان')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='مقاله')),
                ('meta_keywords', models.TextField(null=True, verbose_name='Meta Keywords')),
                ('meta_description', models.TextField(null=True, verbose_name='Meta Description')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ انتشار')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, max_length=100, null=True, unique=True, verbose_name='فیلد URL')),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog', verbose_name='عکس')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='blog', verbose_name='بنر')),
            ],
            options={
                'verbose_name': 'مقاله',
                'verbose_name_plural': 'مقاله ها',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='عنوان')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='توضیحات')),
                ('meta_keywords', models.TextField(null=True, verbose_name='Meta Keywords')),
                ('meta_description', models.TextField(null=True, verbose_name='Meta Description')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ انتشار')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, max_length=100, null=True, unique=True, verbose_name='فیلد URL')),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog', verbose_name='عکس')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='blog', verbose_name='بنر')),
                ('video', models.FileField(upload_to='blog', verbose_name='ویدیو')),
            ],
            options={
                'verbose_name': 'ویدیو',
                'verbose_name_plural': 'ویدیو ها',
            },
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='بازخورد')),
                ('score', models.PositiveSmallIntegerField(verbose_name='امتیاز')),
                ('is_published', models.BooleanField(default=False, verbose_name='انتشار یابد؟')),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.article', verbose_name='مقاله')),
            ],
            options={
                'verbose_name': 'نظرات',
                'verbose_name_plural': 'نظرات',
            },
        ),
    ]
