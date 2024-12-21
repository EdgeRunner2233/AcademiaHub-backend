# Generated by Django 5.1.4 on 2024-12-21 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormList',
            fields=[
                ('form_id_list', models.TextField(default='[]', max_length=1024, verbose_name='未处理的申请的id的列表')),
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='申请处理状态')),
            ],
        ),
        migrations.CreateModel(
            name='NewWorks',
            fields=[
                ('work_id', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='OpenAlexID')),
                ('work_title', models.CharField(max_length=1000, verbose_name='文章题目')),
                ('publication_date', models.DateTimeField(verbose_name='发布时间')),
            ],
        ),
        migrations.CreateModel(
            name='SearchWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100, verbose_name='搜索词条')),
                ('number', models.IntegerField(default=0, verbose_name='词条被搜索次数')),
            ],
        ),
        migrations.CreateModel(
            name='SearchWork',
            fields=[
                ('work_id', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='OpenAlexID')),
                ('work_title', models.CharField(max_length=1000, verbose_name='文章题目')),
                ('number', models.IntegerField(default=0, verbose_name='文章被搜索的次数')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filter', models.CharField(max_length=255)),
                ('publication_year_list', models.JSONField()),
                ('type_list', models.JSONField()),
                ('author_list', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]