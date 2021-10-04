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


class UserFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = '__all__'


class FollowerListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f'{value.user}'


class FollowingListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f'{value.following_user}'


class UserFollowingSerializer(serializers.ModelSerializer):
    following = FollowingListingField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'following')


class UserFollowSerializer(serializers.ModelSerializer):
    followers = FollowerListingField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'followers')


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
                  'created', 'tags', 'comments')

    def create(self, validated_data):
        print(validated_data)
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
