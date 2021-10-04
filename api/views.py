from django.shortcuts import get_object_or_404

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
        {'POST': '/api/users/token/'},
        {'POST': '/api/users/token/refresh/'},
        {'GET': '/api/users/id'},
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


class UserFollowersList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        followers = user.followers.all()
        serializer = UserFollowSerializer(user, many=False)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        user = request.user
        follow = get_object_or_404(User, username=kwargs['user_pk'])
        data = {'user': user.pk, 'following_user': follow.pk, }
        serializer = UserFollowerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFollowingList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_pk'])
        serializer = UserFollowingSerializer(user, many=False)
        return Response(serializer.data)


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
