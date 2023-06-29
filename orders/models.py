from django.db import models

from users.models import ExtendedUser
from django.core.validators import int_list_validator


class Order(models.Model):
    time_of_order = models.DateTimeField()
    user_id = models.IntegerField(null=False)
    delivery_address = models.CharField(max_length=256)
    items_price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_status = models.CharField(max_length=256)
    payment_status = models.CharField(max_length=256)
    goods_ids = models.CharField(max_length=256,
                                 validators=[int_list_validator])
