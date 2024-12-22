from django.db import models

# Create your models here.


class Mark(models.Model):
    user_id = models.BigIntegerField('用户的id')
    # User 实例可以反向访问与之关联的所有 MarkLists
    list_name = models.CharField(max_length=255, verbose_name="列表名称")
    description = models.CharField(max_length=255, verbose_name="描述")
    count = models.IntegerField(default=0, verbose_name="数量")

    class Meta:
        db_table = 'mark_lists'
        indexes = [
            models.Index(fields=['user_id']),          # 为 UserID 字段创建索引，优化查询
            models.Index(fields=['list_name']),     # 可选：为 ListName 字段创建索引
        ]

    def to_dic(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'list_name': self.list_name,
            'description': self.description,
            'count': self.count,
        }


class MarkRelationships(models.Model):
    work_id = models.CharField(max_length=50, verbose_name="OpenAlexID", default='')
    mark_list = models.ForeignKey('mark.Mark', on_delete=models.CASCADE, related_name='mark_list', verbose_name="标记列表ID")
    work_title = models.CharField(max_length=1000, verbose_name='文章题目', default='')
    author_name = models.CharField(max_length=1000, verbose_name="作者姓名", default='')
    cited_by_count = models.IntegerField(verbose_name="引用次数", default=0)
    created_date = models.DateField(verbose_name="被收录时间", default='2024-10-10')
    publication_date = models.DateField(verbose_name="发表时间", default='2024-10-10')
    class Meta:
        db_table = 'mark_relationships'  # 设置数据库表名
        indexes = [
            models.Index(fields=['work_id']),  # 为 WorkID 创建索引
        ]

    def to_dic(self):
        return {
            'id': self.id,
            'work_id': self.work_id,
            'mark_list': self.mark_list.id,
            'work_title': self.work_title,
            'author_name': self.author_name,
            'cited_by_count': self.cited_by_count,
            'created_date': self.created_date,
            'publication_date': self.publication_date,
        }