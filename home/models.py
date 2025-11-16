from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager
from django.contrib.auth.models import Permission

# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    date_joined=models.DateTimeField(default=timezone.now)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions'  # Custom related name to avoid clash
    ) 

    objects=CustomUserManager()
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True, related_name='customuser_set')

    def __str__(self):
        return self.email

