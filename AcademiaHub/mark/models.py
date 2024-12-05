from django.db import models

# Create your models here.


class Mark(models.Model):
    user_id = models.BigIntegerField('用户的id')
    # User 实例可以反向访问与之关联的所有 MarkLists
    list_name = models.CharField(max_length=255, verbose_name="列表名称")
    description = models.CharField(max_length=255, verbose_name="描述")

    class Meta:
        db_table = 'mark_lists'
        indexes = [
            models.Index(fields=['user_id']),          # 为 UserID 字段创建索引，优化查询
            models.Index(fields=['list_name']),     # 可选：为 ListName 字段创建索引
        ]

    def to_dic(self):
        return {
            'id': self.id,
            'user': self.user,
            'list_name': self.list_name,
            'description': self.description,
        }


class MarkRelationships(models.Model):
    work = models.ForeignKey('work.Work', on_delete=models.CASCADE, related_name='mark_relationships', verbose_name="文献ID")
    marklist = models.ForeignKey('mark.Mark', on_delete=models.CASCADE, related_name='mark_relationships', verbose_name="标记列表ID")

    class Meta:
        db_table = 'mark_relationships'  # 设置数据库表名
        indexes = [
            models.Index(fields=['work']),  # 为 WorkID 创建索引
            models.Index(fields=['marklist']),  # 为 MarkListID 创建索引
        ]

    def __str__(self):
        return f"Work: {self.work.id} - MarkList: {self.marklist.id}"