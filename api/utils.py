from tags.models import Tag

from django.forms.models import model_to_dict


def make_dict_from_names(names):
    return [{'name': name} for name in names]

def get_tags_from_dicts(dicts):
    for name_dict in dicts:
        tag, _ = Tag.objects.get_or_create(**name_dict)
        yield  tag