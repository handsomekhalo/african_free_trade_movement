from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from system_management import constants



class UserType(models.Model):
    """
    Defines different types of users:
    - Admin
    - Exporter
    - Logistics Provider
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ensure the superuser flags are set
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Handle the case where the ADMIN role might not exist
        try:
            admin_user_type = UserType.objects.get(name=constants.ADMIN)
            extra_fields.setdefault('user_type', admin_user_type)
        except ObjectDoesNotExist:
            raise ValueError(_(f'{constants.ADMIN} role not found'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Core user model for exporters, logistics providers, and admins.
    """
    username = None
    email = models.EmailField(unique=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    user_created_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.user_type})"
