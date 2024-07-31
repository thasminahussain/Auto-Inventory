from django.db import models

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, verbose_name='Name')
    quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    low_stock_threshold = models.IntegerField(default=0, verbose_name='Low Stock Threshold')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name