from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [
    path('', views.get_routes, name='get_routes'),

    path('users/', views.UsersList.as_view(), name='get_users'),

    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<str:username>/', views.UserDetail.as_view(), name='get_user'),
    path('users/<str:username>/followers/',
         views.UserFollowersList.as_view(), name='get_user_followers'),
    path('users/<str:username>/followers/<str:follower_username>/',
         views.UserFollowerDetail.as_view(), name='get_user_follower'),

    path('users/<str:username>/following/',
         views.UserFollowingList.as_view(), name='get_user_following'),
    path('users/<str:username>/following/<str:following_username>',
         views.UserFollowingDetail.as_view(), name='get_user_following'),

    path('users/<str:username>/posts/',
         views.PostsList.as_view(), name='get_user_posts'),
    path('users/<str:username>/posts/<str:post_pk>/',
         views.PostDetail.as_view(), name='get_user_post'),

    path('users/<str:username>/posts/<str:post_pk>/tags/',
         views.TagsList.as_view(), name='get_user_post_tags'),
    path('users/<str:username>/posts/<str:post_pk>/tags/<str:tag_pk>/',
         views.TagDetail.as_view(), name='get_user_post_tag'),

    path('users/<str:username>/posts/<str:post_pk>/comments/',
         views.CommentsList.as_view(), name='get_user_post_comments'),
    path('users/<str:username>/posts/<str:post_pk>/comments/<str:comment_pk>/',
         views.CommentDetail.as_view(), name='get_user_post_comment'),

    path('users/<str:username>/posts/<str:post_pk>/likes/',
         views.LikesList.as_view(), name='get_user_post_likes'),
    path('users/<str:username>/posts/<str:post_pk>/likes/<str:liked_username>/',
         views.LikeDetail.as_view(), name='get_user_post_like'),


    path('posts/', views.PostsList.as_view(), name='get_posts'),
    path('posts/<str:post_pk>/', views.PostDetail.as_view(), name='get_post'),

    path('posts/<str:post_pk>/tags/',
         views.TagsList.as_view(), name='get_post_tags'),
    path('posts/<str:post_pk>/tags/<str:tag_pk>/',
         views.TagDetail.as_view(), name='get_post_tag'),

    path('posts/<str:post_pk>/likes/',
         views.LikesList.as_view(), name='get_post_likes'),
    path('posts/<str:post_pk>/likes/<str:liked_username>/',
         views.LikeDetail.as_view(), name='get_post_like'),

    path('posts/<str:post_pk>/comments/',
         views.CommentsList.as_view(), name='get_comments'),
    path('posts/<str:post_pk>/comments/<str:comment_pk>/',
         views.CommentDetail.as_view(), name='get_comment'),

    path('tags/', views.TagsList.as_view(), name='get_tags'),
    path('tags/<str:tag_pk>/', views.TagDetail.as_view(), name='get_tag'),
]
