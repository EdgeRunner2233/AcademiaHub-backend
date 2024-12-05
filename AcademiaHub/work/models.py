from django.db import models

# Create your models here.


class Work(models.Model):
    url = models.CharField(max_length=50, verbose_name="路由信息")
    author_name = models.CharField(max_length=50, verbose_name="作者姓名")
    authorship = models.CharField(max_length=50, verbose_name="作者信息API")
    cited_by_count = models.IntegerField(verbose_name="引用次数")
    created_date = models.DateField(verbose_name="被收录时间")
    openalex_id = models.CharField(max_length=50, verbose_name="OpenAlexID")
    publication_year = models.DateField(verbose_name="发表时间")

    class Meta:
        db_table = 'work_lists'
        indexes = [
            models.Index(fields=['author_name']),
            models.Index(fields=['url']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['cited_by_count']),
        ]

    def to_dic(self):
        return {
            'ID': self.ID,
            'url': self.url,
            'authorship': self.authorship,
            'cited_by_count': self.cited_by_count,
            'created_date': self.created_date.strftime('%Y-%m-%d') if self.created_date else None,  # 格式化日期
            'openalex_id': self.openalex_id,
            'publication_year': self.publication_year.strftime('%Y-%m-%d') if self.publication_year else None,  # 格式化日期
        }
