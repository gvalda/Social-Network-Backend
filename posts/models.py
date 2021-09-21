from django.db import models
from django.contrib.auth.models import User
from tags.models import Tag

import uuid
import os


def get_post_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    post = instance.post
    user = post.author

    return os.path.join(str(user), 'posts', str(post.id), filename)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return f'{str(self.author)}: {str(self.description)[:50]}'


class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.ImageField(
        blank=True, null=True, upload_to=get_post_image_path, default='default-images/default.jpg')
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return str(self.post)

    @property
    def get_image(self):
        try:
            url = self.profile_image.url
        except:
            self.profile_image = 'default-images/default.jpg'
            self.save()
            url = self.profile_image.url
        return url
