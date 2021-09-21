from django.contrib.auth.models import User
from users.models import Profile
from posts.models import Post
from tags.models import Tag
from comments.models import Comment

from .utils import *
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('description', 'privacy')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'profile')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True)
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags', 'comments')


class PostSerializerCreate(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags',)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in get_tags_from_dicts(tags_data):
            post.tags.add(tag)
        return post


class PostSerializerUpdate(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags',)

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in get_tags_from_dicts(tags_data):
            post.tags.add(tag)
        return post
