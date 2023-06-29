from django.db import models


class Category(models.Model):
    """TODO add docstr
    """
    title = models.CharField(max_length=256, blank=False, default="some")
