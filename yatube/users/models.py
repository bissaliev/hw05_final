from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель User."""

    avatar = models.ImageField(
        'Фотография', upload_to='users/%Y/%m/%d', null=True, blank=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
