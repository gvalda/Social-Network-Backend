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
    try:
        retrieved_object = model.objects.get(**kwargs)
    except model.DoesNotExist:
        retrieved_object = None
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


def get_user(username):
    return get_object_or_404(User, username=username)


def get_posts(username=None):
    if username:
        user = get_user(username)
        posts = get_list_or_404(Post, author=user)
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
