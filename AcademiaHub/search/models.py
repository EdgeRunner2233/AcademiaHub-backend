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
