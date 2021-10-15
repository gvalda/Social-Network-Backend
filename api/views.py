from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, UserFollowing
from posts.models import Post
from tags.models import Tag
from comments.models import Comment

from .serializers import *
from .utils import *


@api_view(['GET'])
def get_routes(request):
    routes = [
        {'GET': '/api/users'},
        {'POST': '/api/users'},
        {'POST': '/api/users/token/'},
        {'POST': '/api/users/token/refresh/'},
        {'GET': '/api/users/id'},
        {'DELETE': '/api/users/id'},
        {'GET': '/api/users/id/following'},
        {'GET': '/api/users/id/followers'},
        {'POST': '/api/users/id/followers'},
        {'GET': '/api/users/id/posts'},
        {'POST': '/api/users/id/posts'},
        {'GET': '/api/users/id/posts/id'},
        {'PUT': '/api/users/id/posts/id'},
        {'GET': '/api/users/id/posts/id.comments'},
        {'GET': '/api/users/id/posts/id.comments/id'},
        {'GET': '/api/tags'},
        {'GET': '/api/tags/id'},
    ]
    return Response(routes)


class UsersList(APIView):

    def get(self, request, format=None):
        users = get_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, format=None, **kwargs):
        user = get_user(username)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    def patch(self, request, username, format=None, **kwargs):
        instance = get_user(username)
        request_user = request.user
        if instance != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        serializer = UserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username, format=None, **kwargs):
        user = get_user(username)
        request_user = request.user
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class UserFollowersList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, format=None, **kwargs):
        user_followers = get_user_followers(username)
        serializer = UserFollowerSerializer(
            user_followers, many=True, fields=('user',))
        return Response(serializer.data)

    def post(self, request, username, format=None, **kwargs):
        follow = get_user(username)
        user = request.user
        data = {'user': user.pk, 'following_user': follow.pk, }
        serializer = UserFollowerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username, format=None, **kwargs):
        followed_user = get_user(username)
        request_user = request.user
        user_follower = get_user_follower(
            followed_user.username, request_user.username)
        user_follower.delete()
        return Response({'message': f'{request_user.username} is no more following {followed_user.username} in the system'}, status=status.HTTP_204_NO_CONTENT)


class UserFollowerDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, follower_username, format=None, **kwargs):
        user_follower = get_user_follower(username, follower_username)
        serializer = UserFollowerSerializer(
            user_follower, many=False, fields=('user',))
        return Response(serializer.data)

    def delete(self, request, username, follower_username, format=None, **kwargs):
        request_user = request.user
        user = get_user(username)
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_follower = get_user_follower(username, follower_username)
        user_follower.delete()
        return Response({'message': f'{follower_username} is no more following {request_user.username} in the system'}, status=status.HTTP_204_NO_CONTENT)


class UserFollowingList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, format=None, **kwargs):
        user_followings = get_user_followings(username)
        serializer = UserFollowerSerializer(
            user_followings, many=True, fields=('following_user',))
        return Response(serializer.data)


class UserFollowingDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, following_username, format=None, **kwargs):
        user_following = get_user_following(username, following_username)
        serializer = UserFollowerSerializer(user_following, many=False)
        return Response(serializer.data)

    def delete(self, request, username, following_username, format=None, **kwargs):
        request_user = request.user
        user = get_user(username)
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_following = get_user_following(username, following_username)
        user_following.delete()
        return Response({'message': f'{user.username} is no more following {request_user.username} in the system'}, status=status.HTTP_204_NO_CONTENT)


class PostsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        posts = get_posts(username=kwargs.get('username', None))
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        user = request.user
        request.data['author'] = user.id
        tags = request.data.get('tags', [])
        create_not_existing_tags(tags)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, post_pk, format=None, **kwargs):
        post = get_post(post_pk, username=kwargs.get('username', None))
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)

    def patch(self, request, post_pk, format=None, **kwargs):
        instance = get_post(post_pk, username=kwargs.get('username', None))
        user = request.user
        if user != instance.author:
            raise PermissionDenied({"message": "You don't have permission to modify this object",
                                    "post_id": instance.id})
        tags = request.data.get('tags', [])
        create_not_existing_tags(tags)
        serializer = PostSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, format=None, **kwargs):
        instance = get_post(post_pk, username=kwargs.get('username', None))
        user = request.user
        if user != instance.author:
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        instance.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class CommentsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, post_pk, format=None, **kwargs):
        comments = get_comments(
            post_pk=post_pk, username=kwargs.get('username', None))
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_pk, format=None, **kwargs):
        user = request.user
        post = get_post(post_pk, username=kwargs.get('username', None))
        request.data['post'] = post.id
        request.data['author'] = user.id
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, post_pk, comment_pk, format=None, **kwargs):
        comment = get_comment(comment_pk, post_pk=post_pk,
                              username=kwargs.get('username', None))
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data)

    def patch(self, request, post_pk, comment_pk, format=None, **kwargs):
        instance = get_comment(comment_pk, post_pk=post_pk,
                               username=kwargs.get('username', None))
        if request.user != instance.author:
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        serializer = CommentSerializer(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, comment_pk, format=None, **kwargs):
        instance = get_comment(comment_pk, post_pk=post_pk,
                               username=kwargs.get('username', None))
        if request.user != instance.author and request.user != instance.post.author:
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        instance.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class TagsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        tags = get_tags(post_pk=kwargs.get('post_pk', None),
                        username=kwargs.get('username', None))
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class TagDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, tag_pk, format=None, **kwargs):
        tag = get_tag(tag_pk, post_pk=kwargs.get('post_pk', None),
                      username=kwargs.get('username', None))
        serializer = TagSerializer(tag, many=False)
        return Response(serializer.data)


class LikesList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_pk, format=None, **kwargs):
        post = get_post(post_pk, username=kwargs.get('username', None))
        if request.user != post.author:
            raise PermissionDenied(
                {"message": "Only the owner can view post likes", })
        post_likes = post.likes
        serializer = PostLikeSerializer(post_likes, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, post_pk, format=None, **kwargs):
        request_user = request.user
        post = get_post(post_pk, username=kwargs.get('username', None))
        data = {
            'post': post.pk,
            'liked_user': request_user.pk,
        }
        serializer = PostLikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, post_pk, liked_username, format=None, **kwargs):

        user = get_user(liked_username)
        if request.user != user:
            raise PermissionDenied(
                {"message": "Only the author of a like can remove it from the post", })
        liked_user = get_liked_user(
            liked_username, post_pk, post_author_username=kwargs.get(
                'username', None))
        liked_user.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
