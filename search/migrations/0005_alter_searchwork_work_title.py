# Generated by Django 4.2.4 on 2024-12-08 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_rename_work_name_searchwork_work_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchwork',
            name='work_title',
            field=models.CharField(max_length=1000, verbose_name='文章题目'),
        ),
    ]
