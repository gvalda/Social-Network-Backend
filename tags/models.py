from django.db import models


class Tag(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50,
                            unique=True, primary_key=True)

    def __str__(self):
        return self.name
