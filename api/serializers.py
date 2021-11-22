from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Profile, UserFollowing
from posts.models import Post, PostLike
from tags.models import Tag
from comments.models import Comment

from .utils import *
from rest_framework import serializers


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff
        return data


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
            'profile': {'required': False, },
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


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserFollowerSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ('user', 'following_user',)

    def to_representation(self, value):
        data = super(UserFollowerSerializer, self).to_representation(value)
        user_id = data.get('user', None)
        if user_id:
            user = get_object_or_none(User, id=user_id)
            if user:
                data.update(user=user.username)
        following_user_id = data.get('following_user', None)
        if following_user_id:
            following_user = get_object_or_none(User, id=following_user_id)
            if following_user:
                data.update(following_user=following_user.username)
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {'post': {'write_only': True}}

    def to_representation(self, value):
        data = super(CommentSerializer, self).to_representation(value)
        author_id = data.get('author', None)
        if author_id:
            author = get_object_or_none(User, id=author_id)
            if author:
                data.update(author=author.username)
        return data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'author', 'description',
                  'created', 'tags', 'comments', 'likes_number')
        extra_kwargs = {'comments': {'required': False}}

    def to_representation(self, value):
        data = super(PostSerializer, self).to_representation(value)
        author_id = data.get('author', None)
        author_username = get_username_from_id(author_id)
        if author_username:
            data.update(author=author_username)
        comments_ids = data.get('comments', None)
        if comments_ids:
            comments = []
            for comment_id in comments_ids:
                comment = get_object_or_none(Comment, id=comment_id)
                comment_dict = model_to_dict(comment)
                comment_dict.pop('post')
                author_id = comment_dict.get('author', None)
                author_username = get_username_from_id(author_id)
                if author_username:
                    comment_dict.update(author=author_username)
                comments.append(comment_dict)
            data.update(comments=comments)
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
