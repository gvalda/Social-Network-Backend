from rest_framework import status
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from api.mixins import CustomPaginationMixin

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
        {'PATCH': '/api/users/id'},
        {'DELETE': '/api/users/id'},
        {'GET': '/api/users/id/following'},
        {'GET': '/api/users/id/following/id'},
        {'DELETE-': '/api/users/id/following/id'},
        {'GET': '/api/users/id/followers'},
        {'POST': '/api/users/id/followers'},
        {'DELETE': '/api/users/id/followers'},
        {'GET': '/api/users/id/followers/id'},
        {'DELETE': '/api/users/id/followers/id'},
        {'POST': '/api/users/id/followers'},
        {'GET': '/api/users/id/posts'},
        {'POST': '/api/users/id/posts'},
        {'GET': '/api/users/id/posts/id'},
        {'PATCH': '/api/users/id/posts/id'},
        {'DELETE': '/api/users/id/posts/id'},
        {'GET': '/api/users/id/posts/id/comments'},
        {'POST': '/api/users/id/posts/id/comments'},
        {'GET': '/api/users/id/posts/id/comments/id'},
        {'PATCH': '/api/users/id/posts/id/comments/id'},
        {'DELETE': '/api/users/id/posts/id/comments/id'},
        {'GET': '/api/users/id/posts/id/likes'},
        {'POST': '/api/users/id/posts/id/likes'},
        {'DELETE': '/api/users/id/posts/id/likes/id'},
        {'GET': '/api/users/id/posts/id/tags'},
        {'GET': '/api/users/id/posts/id/tags/id'},
    ]
    return Response(routes)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UsersList(APIView):
    serializer_class = UserSerializer

    def get(self, request, format=None):
        users = get_users()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    def get(self, request, username, format=None, **kwargs):
        user = get_user(username)
        serializer = self.serializer_class(user, many=False)
        return Response(serializer.data)

    def patch(self, request, username, format=None, **kwargs):
        instance = get_user(username)
        request_user = request.user
        if instance != request_user or not is_superuser(request_user):
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username, format=None, **kwargs):
        user = get_user(username)
        request_user = request.user
        if user != request_user or not is_superuser(request_user):
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_200_OK)


class UserFollowersList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowerSerializer

    def get(self, request, username, format=None, **kwargs):
        user_followers = get_user_followers(username)
        serializer = self.serializer_class(
            user_followers, many=True, fields=('user',))
        return Response(serializer.data)

    def post(self, request, username, format=None, **kwargs):
        follow = get_user(username)
        user = request.user
        data = {'user': user.pk, 'following_user': follow.pk, }
        serializer = self.serializer_class(data=data)
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
        return Response({'message': f'{request_user.username} is no more following {followed_user.username} in the system'}, status=status.HTTP_200_OK)


class UserFollowerDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowerSerializer

    def get(self, request, username, follower_username, format=None, **kwargs):
        user_follower = get_user_follower(username, follower_username)
        serializer = self.serializer_class(
            user_follower, many=False, fields=('user',))
        return Response(serializer.data)

    def delete(self, request, username, follower_username, format=None, **kwargs):
        request_user = request.user
        user = get_user(username)
        if user != request_user or not is_superuser(request_user):
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_follower = get_user_follower(username, follower_username)
        user_follower.delete()
        return Response({'message': f'{follower_username} is no more following {request_user.username} in the system'}, status=status.HTTP_200_OK)


class UserFollowingList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowerSerializer

    def get(self, request, username, format=None, **kwargs):
        user_followings = get_user_followings(username)
        serializer = self.serializer_class(
            user_followings, many=True, fields=('following_user',))
        return Response(serializer.data)


class UserFollowingDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowerSerializer

    def get(self, request, username, following_username, format=None, **kwargs):
        user_following = get_user_following(username, following_username)
        serializer = self.serializer_class(user_following, many=False)
        return Response(serializer.data)

    def delete(self, request, username, following_username, format=None, **kwargs):
        request_user = request.user
        user = get_user(username)
        if user != request_user or not is_superuser(request_user):
            raise PermissionDenied({"message": "You don't have permission to modify",
                                    "user": request_user.username, })
        user_following = get_user_following(username, following_username)
        user_following.delete()
        return Response({'message': f'{user.username} is no more following {request_user.username} in the system'}, status=status.HTTP_200_OK)


class PostsList(APIView, CustomPaginationMixin):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = PostSerializer

    def get(self, request, format=None, **kwargs):
        posts = get_posts(username=kwargs.get('username', None))
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    def post(self, request, format=None, **kwargs):
        user = request.user
        request.data['author'] = user.id
        tags = request.data.get('tags', [])
        create_not_existing_tags(tags)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = PostSerializer

    def get(self, request, post_pk, format=None, **kwargs):
        post = get_post(post_pk, username=kwargs.get('username', None))
        serializer = self.serializer_class(post, many=False)
        return Response(serializer.data)

    def patch(self, request, post_pk, format=None, **kwargs):
        instance = get_post(post_pk, username=kwargs.get('username', None))
        user = request.user
        if not is_author_or_superuser(user, instance):
            raise PermissionDenied({"message": "You don't have permission to modify this object",
                                    "post_id": instance.id})
        tags = request.data.get('tags', [])
        create_not_existing_tags(tags)
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, format=None, **kwargs):
        instance = get_post(post_pk, username=kwargs.get('username', None))
        user = request.user
        if not is_author_or_superuser(user, instance):
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        instance.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_200_OK)


class CommentsList(APIView, CustomPaginationMixin):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = CommentSerializer

    def get(self, request, post_pk, format=None, **kwargs):
        comments = get_comments(
            post_pk=post_pk, username=kwargs.get('username', None))
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    def post(self, request, post_pk, format=None, **kwargs):
        user = request.user
        post = get_post(post_pk, username=kwargs.get('username', None))
        request.data['post'] = post.id
        request.data['author'] = user.id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer

    def get(self, request, post_pk, comment_pk, format=None, **kwargs):
        comment = get_comment(comment_pk, post_pk=post_pk,
                              username=kwargs.get('username', None))
        serializer = self.serializer_class(comment, many=False)
        return Response(serializer.data)

    def patch(self, request, post_pk, comment_pk, format=None, **kwargs):
        request_user = request.user
        instance = get_comment(comment_pk, post_pk=post_pk,
                               username=kwargs.get('username', None))
        if not is_author_or_superuser(request_user, instance):
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, comment_pk, format=None, **kwargs):
        request_user = request.user
        instance = get_comment(comment_pk, post_pk=post_pk,
                               username=kwargs.get('username', None))
        if not is_author_or_superuser(request_user, instance) and not is_author_or_superuser(request_user, instance.post):
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "post_id": instance.id})
        instance.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_200_OK)


class TagsList(APIView, CustomPaginationMixin):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = TagSerializer

    def get(self, request, format=None, **kwargs):
        tags = get_tags(post_pk=kwargs.get('post_pk', None),
                        username=kwargs.get('username', None))
        page = self.paginate_queryset(tags)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)


class TagDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer

    def get(self, request, tag_name, format=None, **kwargs):
        tag = get_tag(tag_name, post_pk=kwargs.get('post_pk', None),
                      username=kwargs.get('username', None))
        serializer = self.serializer_class(tag, many=False)
        return Response(serializer.data)


class LikesList(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostLikeSerializer

    def get(self, request, post_pk, format=None, **kwargs):
        post = get_post(post_pk, username=kwargs.get('username', None))
        if request.user != post.author:
            raise PermissionDenied(
                {"message": "Only the owner can view post likes", })
        post_likes = post.likes
        serializer = self.serializer_class(post_likes, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, post_pk, format=None, **kwargs):
        request_user = request.user
        post = get_post(post_pk, username=kwargs.get('username', None))
        data = {
            'post': post.pk,
            'liked_user': request_user.pk,
        }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, post_pk, liked_username, format=None, **kwargs):
        request_user = request.user
        user = get_user(liked_username)
        if request_user != user or not is_superuser(request_user):
            raise PermissionDenied(
                {"message": "Only the author of a like can remove it from the post", })
        liked_user = get_liked_user(
            liked_username, post_pk, post_author_username=kwargs.get(
                'username', None))
        liked_user.delete()
        return Response({'message': f'Instance was successfully deleted'}, status=status.HTTP_200_OK)
