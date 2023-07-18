from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ExtendedUser(AbstractUser):
    # roles are: 1-user. 2-seller. 3-admin
    role = models.IntegerField(blank=False, default=1, validators=[
        MinValueValidator(1), MaxValueValidator(3)])
    address = models.CharField(max_length=256, null=True)
    firstName = models.CharField(max_length=256, null=True)
    lastName = models.CharField(max_length=256, null=True)
    image = models.CharField(max_length=5000, null=True, blank=True)
    sub = models.CharField(max_length=256, null=True)

    def is_user(self):
        return self.role == 1

    def is_seller(self):
        return self.role == 2

    def is_admin(self):
        return self.role == 3
