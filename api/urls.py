from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [
    path('', views.get_routes, name='get_routes'),
    path('users/', views.get_users, name='get_users'),
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<str:user_pk>/', views.get_user, name='get_user'),
    path('users/<str:user_pk>/posts/', views.get_posts, name='get_posts'),
    path('users/<str:user_pk>/posts/<str:post_pk>/',
         views.get_post, name='get_post'),
    path('users/<str:user_pk>/posts/<str:post_pk>/comments/',
         views.get_comments, name='get_comments'),
    path('users/<str:user_pk>/posts/<str:post_pk>/comments/<str:comment_pk>/',
         views.get_comment, name='get_comment'),
    path('tags/', views.get_tags, name='get_tags'),
    path('tags/<str:tag_pk>/', views.get_tag, name='get_tag'),
]
