from random import choice

from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.template.defaultfilters import default
from django.contrib.auth.hashers import make_password


class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, realname, email, password, **extra_fields):

        if not realname:
            raise ValueError("It is necessary to enter your real name.")
        email = self.normalize_email(email)
        user = self.model(username=realname, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    create_superuser.alters_data = True


    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth.get_backends()
            if len(backends) == 1:
                backend = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


# Rewrite the user model
class UserStatusChoices(models.IntegerChoices):
    # Activated already
    ACTIVED = 1
    UNACTIVE = 2
    LOCKED = 3

class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """


    realname = models.CharField(max_length=150,unique=False,)
    email = models.EmailField(unique=True, blank=False)
    telephone = models.CharField(max_length=20, blank=True,unique=True)
    is_staff = models.BooleanField(default=True)

    status = models.IntegerChoices(choices = UserStatusChoices,default = UserStatusChoices.UNACTIVE)

    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = OAUserManager()

    EMAIL_FIELD = "email"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

