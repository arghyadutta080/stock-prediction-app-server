from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.

class User(AbstractUser):
    username = None
    # extra_data = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    phone_number = models.CharField(max_length=10, unique=True)
    isPhoneVerified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    last_searched_stock = models.CharField(max_length=10, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager() 