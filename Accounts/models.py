from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The given email must be set'))

        if not first_name or not last_name:
            raise ValueError(_('The given first name and last name must be set'))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('staff must be True'))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('superuser must be True'))

        if not password:
            raise ValueError(_("Superusers must have a password"))

        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=False, blank=False, null=False)
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email Address"), max_length=254, unique=True)
    phone_number = models.CharField(_("Phone Number"), unique=True, max_length=100, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    picture_key = models.CharField(_("Picture Key"), max_length=254, blank=True, null=True)
    reset_password_token = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('inactive', 'InActive'),
        ('active', 'Active'),
        ('block', 'Block'),
        ('delete', 'Delete'),
    ], default='inactive')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def formatted_last_login(self):
        if self.last_login:
            local_last_login = timezone.localtime(self.last_login)
            return local_last_login.strftime('%H:%M:%S %d-%m-%Y')
        return "Never logged in"


# class Queries(models.Model):
#     query = models.TextField(null=True, blank=True)
#     name = models.TextField(null=True, blank=True, max_length=150)
#     email = models.EmailField()
#     phone_number = models.CharField()
#     message = models.TextField()
#     date_created = models.DateTimeField(auto_now_add=True)


class Chats(models.Model):
    user_id = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)


class Messages(models.Model):
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)

