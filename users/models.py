from django.db import models
from django.contrib.auth.models import User

import os
import uuid


def get_user_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(str(instance.user), filename)


class Profile(models.Model):
    PRIVATE = 'PRIV'
    PUBLIC = 'PUBL'

    PRIVACY_CHOICES = [
        (PRIVATE, 'Private'),
        (PUBLIC, 'Public'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        blank=True, null=True, upload_to=get_user_image_path, default='default-images/default.jpg')
    privacy = models.CharField(
        max_length=4, choices=PRIVACY_CHOICES, default=PUBLIC)

    def __str__(self):
        return str(self.user)

    @property
    def get_image(self):
        try:
            url = self.profile_image.url
        except:
            self.profile_image = 'default-images/default.jpg'
            self.save()
            url = self.profile_image.url
        return url
