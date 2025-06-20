from __future__ import unicode_literals

# Create your models here.
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from users.managers import UserManager
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.template.loader import render_to_string


class User(AbstractBaseUser, PermissionsMixin):
    # These fields tie to the roles!
    ADMIN = 1
    OPERATION = 2
    FINANACE = 3
    FINANACE_HEAD = 4

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (OPERATION, 'Operation'),
        (FINANACE, 'Finance'),
        (FINANACE_HEAD , 'Finance Head')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    external_user = models.CharField(_('external user'), max_length=255, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    send_notification = models.BooleanField(default=False)
    country = models.CharField(max_length=255, blank=True , null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def get_user_id(self):
        '''
        Returns the id for the user.
        '''
        return self.id

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Countries(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    country_code = models.CharField(max_length=255 , null=True)
    country_name = models.CharField(max_length=255 , null=True)
    display_level = models.IntegerField()

    class Meta:
        db_table = 'countries'
        verbose_name = "countries"
        verbose_name_plural = "countries"

    def __str__(self):
        return str(self.country_name)


class UserCountries(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_name = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    country_name = models.ForeignKey(Countries, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey('users.User', related_name='%(class)s_created_by', null=True,
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('users.User', related_name='%(class)s_updated_by', null=True,
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_countries'
        verbose_name = "users_countries"
        verbose_name_plural = "users_countries"


"""class UserPermission(models.Model):
    user_id = models.CharField(max_length=255, null=True)
    permission_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'users_user_user_permissions'
        verbose_name = "users_user_user_permissions"""


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.first_name,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            # instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            # 'https://staff.opallius.com/reset-password',
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="ATS user"),
        # message:
        email_html_message,
        # from:
        "noreply@opallios.cloud",
        # to:
        [reset_password_token.user.email]
    )
