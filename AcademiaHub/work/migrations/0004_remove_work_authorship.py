# Generated by Django 4.2.4 on 2024-12-09 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0003_remove_work_work_lists_openale_be7912_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='authorship',
        ),
    ]