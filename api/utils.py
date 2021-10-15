from tags.models import Tag

from django.forms.models import model_to_dict
from django.shortcuts import get_list_or_404, get_object_or_404

from users.models import User, UserFollowing
from posts.models import Post
from tags.models import Tag
from comments.models import Comment


def create_not_existing_tags(tags):
    for tag in tags:
        Tag.objects.get_or_create(name=tag)


def get_object_or_none(model, **kwargs):
    retrieved_object = None
    try:
        retrieved_object = model.objects.get(**kwargs)
    except model.DoesNotExist:
        pass
    return retrieved_object


def get_username_from_id(id):
    if id:
        user = get_object_or_none(User, id=id)
        if user:
            username = user.username
            return username
    return None


def update_object(object, **kwargs):
    for key, value in kwargs.items():
        setattr(object, key, value)
    object.save()


def make_dict_from_names(names):
    return [{'name': name} for name in names]


def get_tags_from_dicts(dicts):
    for name_dict in dicts:
        tag, _ = Tag.objects.get_or_create(**name_dict)
        yield tag


def get_users():
    users = User.objects.all()
    return users


def get_user(username):
    return get_object_or_404(User, username=username)


def get_posts(username=None):
    if username:
        user = get_user(username)
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.all()
    return posts


def get_post(post_pk, username=None):
    posts = get_posts(username)
    post = get_object_or_404(posts, pk=post_pk)
    return post


def get_comments(post_pk, username=None):
    post = get_post(post_pk, username)
    comments = post.comments.all()
    return comments


def get_comment(comment_pk, post_pk, username=None):
    comments = get_comments(post_pk, username)
    comment = get_object_or_404(comments, pk=comment_pk)
    return comment


def get_tags(post_pk=None, username=None):
    if post_pk:
        post = get_post(post_pk, username)
        tags = post.tags.all()
    else:
        tags = Tag.objects.all()
    return tags


def get_tag(tag_pk, post_pk=None, username=None):
    tags = get_tags(post_pk, username)
    tag = get_object_or_404(tags, pk=tag_pk)
    return tag


def get_liked_user(liked_username, post_pk, post_author_username):
    post = get_post(post_pk, username=post_author_username)
    likes = post.likes.all()
    liked_user = get_user(liked_username)
    post_like = get_object_or_404(likes, liked_user=liked_user)
    return post_like


def get_user_followers(username):
    user = get_user(username)
    user_followers = user.followers.all()
    return user_followers


def get_user_follower(username, follower_username):
    user_followers = get_user_followers(username)
    followed_user = get_user(follower_username)
    user_follower = get_object_or_404(
        user_followers, user=followed_user)
    return user_follower


def get_user_followings(username):
    user = get_user(username)
    user_followings = user.following.all()
    return user_followings


def get_user_following(username, following_username):
    user_followings = get_user_followings(username)
    followed_user = get_user(following_username)
    user_following = get_object_or_404(
        user_followings, following_user=followed_user)
    return user_following
