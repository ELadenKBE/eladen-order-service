from django.contrib.postgres.fields import ArrayField
from django.db import models

from users.models import ExtendedUser


class Order(models.Model):
    time_of_order = models.DateTimeField()
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=256)
    items_price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_status = models.CharField(max_length=256)
    payment_status = models.CharField(max_length=256)
    goods_ids = ArrayField(models.IntegerField(null=False, blank=True),
                       null=True, blank=True)

