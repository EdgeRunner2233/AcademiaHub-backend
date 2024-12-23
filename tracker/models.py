from django.db import models

# Create your models here.
class TrackerList(models.Model):
    user_id = models.BigIntegerField('用户的id')
    tracker_name = models.CharField('跟踪器', max_length=100)
    para = models.CharField('搜索参数', max_length=100)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def to_dic(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tracker_name': self.tracker_name,
            'para': self.para,
            'create_time': self.create_time,
        }