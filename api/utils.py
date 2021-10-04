from tags.models import Tag

from django.forms.models import model_to_dict
from django.http import Http404

from users.models import Profile


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
