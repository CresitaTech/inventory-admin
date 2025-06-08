from __future__ import unicode_literals

# Create your models here.
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
# from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# from users.managers import UserManager
from django.dispatch import receiver
from django.urls import reverse
# from django_rest_passwordreset.signals import reset_password_token_created
# from django.core.mail import send_mail
# from django.template.loader import render_to_string


# class User(AbstractBaseUser, PermissionsMixin):
class User(AbstractUser):
    # These fields tie to the roles!
    ADMIN = 1
    OPERATOR = 2
    FINANCIER = 3
    CFO = 4

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (OPERATOR, 'Operator'),
        (FINANCIER, 'Financier'),
        (CFO , 'Cfo')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(('email address'), unique=True)
    external_user = models.CharField(('external user'), max_length=255, blank=True)
    first_name = models.CharField(('first name'), max_length=30, blank=True)
    last_name = models.CharField(('last name'), max_length=30, blank=True)
    send_notification = models.BooleanField(default=False)
    country = models.CharField(max_length=255, blank=True , null=True)
    date_joined = models.DateTimeField(('date joined'), auto_now_add=True)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
    #                                on_delete=models.CASCADE)
    # updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                #    on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    # objects = UserManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    
    
class InventoryItem(models.Model):
    warehouse = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    item_number = models.CharField(max_length=255)
    item_name = models.CharField(max_length=255)
    lot_number = models.CharField(max_length=100)
    expiration_date = models.CharField(max_length=20)
    quantity = models.FloatField()
    uom = models.CharField(max_length=20)  # UOM = Unit of Measure
    price = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=12, decimal_places=2)

    # def __str__(self):
    #     return f"{self.item_name} - {self.lot_number}"
    
    class Meta:
        db_table = 'inventory_items'  