from django.db import models

# Create your models here.

class FormList(models.Model):
    form_id_list = models.TextField('未处理的申请的id的列表', max_length=1024, default='[]')
    id = models.IntegerField('申请处理状态', primary_key=True)  # 0表示正在审批，1表示申请通过，2表示申请拒绝

    def to_dic(self):
        return {
            'id': self.id,
            'Form_id_list': eval(self.form_id_list),
        }

class SearchWork(models.Model):
    work_id = models.CharField('OpenAlexID', max_length=50, primary_key=True)
    work_title = models.CharField('文章题目', max_length=1000)
    number = models.IntegerField('文章被搜索的次数', default=0)

    def to_dic(self):
        return {
            'work_id': self.work_id,
            'work_name': self.work_title,
            'number': self.number,
        }

class SearchWord(models.Model):
    word = models.CharField('搜索词条', max_length=100)
    number = models.IntegerField('词条被搜索次数', default=0)

    def to_dic(self):
        return {
            'word': self.word,
            'number': self.number,
        }

class NewWorks(models.Model):
    work_id = models.CharField('OpenAlexID', max_length=50, primary_key=True)
    created_time = models.DateTimeField('被收录时间')

    def to_dic(self):
        return {
            'work_id': self.work_id,
            'created_time': self.created_time,
        }