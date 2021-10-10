from django.contrib import admin
from .models import *


class PostPhotoInline(admin.TabularInline):
    model = PostPhoto


class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)

    inlines = [
        PostPhotoInline,
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(PostPhoto)
admin.site.register(PostLike)
