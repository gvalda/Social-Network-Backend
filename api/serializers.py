from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from users.models import Profile, UserFollowing
from posts.models import Post, PostLike
from tags.models import Tag
from comments.models import Comment

from .utils import *
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('description',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'profile', 'password')
        extra_kwargs = {
            'password': {'write_only': True, },
            'profile': {'required': False, }
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        profile = Profile.objects.get(user=user)
        update_object(profile, **profile_data)
        user.refresh_from_db()
        return user


class UserFollowerSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ('user', 'following_user',)

    def to_representation(self, value):
        data = super(UserFollowerSerializer, self).to_representation(value)
        user_id = data.get('user', None)
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            data.update(user=user.username)
        following_user_id = data.get('following_user', None)
        if following_user_id:
            following_user = get_object_or_404(User, pk=following_user_id)
            data.update(following_user=following_user.username)
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'post': {'required': False}}

    def create(self, validated_data):
        author = self.initial_data.get('author', None)
        if author:
            validated_data['author'] = author
        comment = Comment.objects.create(**validated_data)
        comment.save()
        return comment

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False)
    author = serializers.StringRelatedField(source='author.username')

    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags', 'comments', 'likes_number')

    def create(self, validated_data):
        author = self.initial_data.get('author', None)
        if author:
            validated_data['author'] = author
        tags_data = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in get_tags_from_dicts(tags_data):
            post.tags.add(tag)
        post.save()
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        instance.description = validated_data.get(
            'description', instance.description)
        for tag in get_tags_from_dicts(tags_data):
            instance.tags.add(tag)
        instance.save()
        return instance

    def to_representation(self, value):
        data = super(PostSerializer, self).to_representation(value)
        tags = data.get('tags')
        tag_names = [tag.get('name') for tag in tags]
        comments = data.get('comments')
        for comment in comments:
            comment.pop('post')
        data.update(tags=tag_names, comments=comments)
        return data


class PostLikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='liked_user.username', read_only=True)

    class Meta:
        model = PostLike
        fields = ('username', 'liked_user', 'post',)
        extra_kwargs = {
            'post': {'write_only': True, },
            'liked_user': {'write_only': True, },
        }
