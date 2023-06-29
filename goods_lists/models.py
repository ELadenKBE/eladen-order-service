from django.db import models

from goods.models import Good
from users.models import ExtendedUser


class GoodsList(models.Model):
    title = models.CharField(max_length=256, blank=False)
    user = models.ForeignKey(ExtendedUser,
                             on_delete=models.CASCADE,
                             blank=False,
                             null=True)
    goods = models.ManyToManyField(Good)
