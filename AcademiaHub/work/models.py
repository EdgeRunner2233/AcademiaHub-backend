from django.db import models

# Create your models here.


class Work(models.Model):
    work_id = models.CharField(max_length=50, verbose_name="OpenAlexID", primary_key=True)
    author_name = models.CharField(max_length=1000, verbose_name="作者姓名")
    cited_by_count = models.IntegerField(verbose_name="引用次数")
    created_date = models.DateField(verbose_name="被收录时间")
    publication_year = models.DateField(verbose_name="发表时间")


    class Meta:
        db_table = 'work_lists'
        indexes = [
            models.Index(fields=['author_name']),
            models.Index(fields=['work_id']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['cited_by_count']),
        ]

    def to_dic(self):
        return {
            'work_id': self.work_id,
            'authorship': self.authorship,
            'cited_by_count': self.cited_by_count,
            'created_date': self.created_date.strftime('%Y-%m-%d') if self.created_date else None,  # 格式化日期
            'publication_year': self.publication_year.strftime('%Y-%m-%d') if self.publication_year else None,  # 格式化日期
        }
