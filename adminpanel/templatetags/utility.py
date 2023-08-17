from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter()
def slicer(value, arg):
    return value[arg]

@register.filter()
def titLe(value):
    return value.title()

@register.filter()
def getListFromQueryDict(querydict, itemToGet):
    return querydict.getlist(itemToGet)

@register.filter()
def querysetToPrimaryKey(queryset):
    return list(map(lambda x: x.pk, queryset))

@register.filter
def user_check(value):
    return value.content_type.model_class() is User

@register.filter
def obj_exists(value):
    return value.content_type.model_class().objects.filter(pk=value.object_id).exists()

@register.filter
def model_name(value):
    return value.name.title()

@register.filter
def multiply(value, arg):
    return value * arg
