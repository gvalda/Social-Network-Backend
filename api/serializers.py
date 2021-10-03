from django.contrib.auth.models import User
from users.models import Profile, UserFollowing
from posts.models import Post
from tags.models import Tag
from comments.models import Comment

from .utils import *
from rest_framework import serializers


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
        extra_kwargs = {'password': {'write_only': True, }}

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


class FollowerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = UserFollowing
        fields = ('user', )

    def create(self, validated_data):
        user = self.initial_data.get('user', None)
        follow = self.initial_data.get('follow', None)
        user_following = UserFollowing.objects.create(
            user=user, following_user=follow)
        user_following.save()
        return user_following


class FollowingSerializer(serializers.ModelSerializer):
    following_user = serializers.StringRelatedField(many=False)

    class Meta:
        model = UserFollowing
        fields = ('following_user',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = '__all__'

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
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags', 'comments')

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
