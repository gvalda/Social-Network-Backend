from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
        users = User.objects.all()
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

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    def put(self, request, format=None, **kwargs):
        instance = get_object_or_404(User, username=kwargs['user_pk'])
        request_user = request.user
        if instance != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        serializer = UserSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        request_user = request.user
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class UserFollowersList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        serializer = UserFollowSerializer(user, many=False)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        follow = get_object_or_404(User, username=kwargs['user_pk'])
        user = request.user
        data = {'user': user.pk, 'following_user': follow.pk, }
        serializer = UserFollowerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFollowerDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        follower_user = get_object_or_404(User, username=kwargs['follower_pk'])
        user_following = get_object_or_404(
            UserFollowing, user=follower_user,     following_user=user)
        serializer = UserFollowerSerializer(user_following, many=False)
        return Response(serializer.data)

    def delete(self, request, format=None, **kwargs):
        request_user = request.user
        user = get_object_or_404(User, username=kwargs['user_pk'])
        follower_user = get_object_or_404(User, username=kwargs['follower_pk'])
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_follower = get_object_or_404(
            UserFollowing, user=follower_user, following_user=user)
        user_follower.delete()
        return Response({'message': f'{user.username} is no more following {request_user.username} in the system'}, status=status.HTTP_204_NO_CONTENT)


class UserFollowingList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        serializer = UserFollowingSerializer(user, many=False)
        return Response(serializer.data)


class UserFollowingDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        following_user = get_object_or_404(
            User, username=kwargs['follower_pk'])
        user_following = get_object_or_404(
            UserFollowing, user=user, following_user=following_user)
        serializer = UserFollowerSerializer(user_following, many=False)
        return Response(serializer.data)

    def delete(self, request, format=None, **kwargs):
        request_user = request.user
        user = get_object_or_404(User, username=kwargs['user_pk'])
        following_user = get_object_or_404(
            User, username=kwargs['following_pk'])
        if user != request_user:
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_following = get_object_or_404(
            UserFollowing, user=user, following_user=following_user)
        user_following.delete()
        return Response({'message': f'{user.username} is no more following {request_user.username} in the system'}, status=status.HTTP_204_NO_CONTENT)


class PostsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        if 'user_pk' in kwargs:
            user = get_object_or_404(User, username=kwargs['user_pk'])
            posts = user.post_set.all()
        else:
            posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        request.data['author'] = user
        tags = make_dict_from_names(request.data['tags'])
        request.data['tags'] = tags
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None, **kwargs):
        if 'user_pk' in kwargs:
            user = get_object_or_404(User, username=kwargs['user_pk'])
            post = get_object_or_404(Post, author=user, pk=kwargs['post_pk'])
        else:
            post = get_object_or_404(Post, pk=kwargs['post_pk'])
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)

    def put(self, request, format=None, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_pk'])
        user = request.user
        if user != instance.author:
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        serializer = PostSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_pk'])
        user = request.user
        if user != instance.author:
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        instance.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class CommentsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None, **kwargs):
        if 'post_pk' in kwargs:
            post = get_object_or_404(Post, id=kwargs['post_pk'])
            comments = post.comments.all()
        else:
            comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        user = request.user
        post = get_object_or_404(Post, id=kwargs['post_pk'])
        request.data['post'] = post.id
        request.data['author'] = user
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        if 'post_pk' in kwargs:
            comment = get_object_or_404(Comment,
                                        id=kwargs['comment_pk'], post=kwargs['post_pk'])
        else:
            comment = Comment.objects.get(id=kwargs['comment_pk'])
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data)

    def put(self, request, format=None, **kwargs):
        if 'post_pk' in kwargs:
            instance = Comment.objects.get(
                id=kwargs['comment_pk'], post=kwargs['post_pk'])
        else:
            instance = Comment.objects.get(id=kwargs['comment_pk'])
        serializer = CommentSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        if 'post_pk' in kwargs:
            post = get_object_or_404(Post, id=kwargs['post_pk'])
            tags = post.tags.all()
        else:
            tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class TagDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        if 'post_pk' in kwargs:
            post = get_object_or_404(Post, id=kwargs['post_pk'])
            tags = get_object_or_404(post.tags, id=kwargs['tag_pk'])
        else:
            tag = get_object_or_404(Tag, id=kwargs['tag_pk'])
        serializer = TagSerializer(tag, many=False)
        return Response(serializer.data)
