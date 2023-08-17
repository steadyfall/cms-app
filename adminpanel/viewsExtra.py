from django.forms.widgets import CheckboxSelectMultiple
from django.db.models.fields import BigAutoField, CharField
from django.db import models
import re
import datetime


# Useful functions
def safe_object_delete(model, pk: str | int) -> None:
    """
    Safely deletes an object using its primary key, if in valid format (only digits)
    or else returns (0, None) to align with future operations.
    """
    return model.objects.get(pk=pk).delete()


def pk_checker(pk: int | str, model: models.Model) -> bool:
    """
    Checks if the given primary key qualifies as a primary key.
    """
    if isinstance(model._meta.pk, BigAutoField):
        return pk.isdigit()
    elif isinstance(model._meta.pk, CharField):
        RANDOM_STRING_CHARS = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        pattern = "[{}]".format(RANDOM_STRING_CHARS) + "{8}"
        return re.fullmatch(pattern, pk) is not None
    else:
        return pk.isdigit()


def safe_pk_list_converter(pk_list: list, model: models.Model) -> list:
    """
    Safely converts a string to number and 0 if not in digits to return a list of numbers.
    """
    if isinstance(model._meta.pk, BigAutoField):
        return list(map(lambda x: int(x) if pk_checker(x, model) else 0, pk_list))
    elif isinstance(model._meta.pk, CharField):
        return list(map(lambda x: x if pk_checker(x, model) else 0, pk_list))
    else:
        return list(map(lambda x: int(x) if pk_checker(x, model) else 0, pk_list))


def widget_list_generator(model):
    """
    Creates a widget dictionary for the ModelForm, based on the model.
    """

    widget_dict = {}
    for field in model._meta.get_fields():
        if field.is_relation and field.many_to_many:
            widget_dict[field.name] = CheckboxSelectMultiple()
    return widget_dict


def get_content_type_for_model(obj):
    # Since this module gets imported in the application's root package,
    # it cannot import models from other applications at the module level.
    from django.contrib.contenttypes.models import ContentType

    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def log_addition(request, obj, message):
    """
    Log that an object has been successfully added.

    """
    from django.contrib.admin.models import ADDITION, LogEntry

    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=ADDITION,
        change_message=message,
    )


def log_change(request, obj, message):
    """
    Log that an object has been successfully changed.

    """
    from django.contrib.admin.models import CHANGE, LogEntry

    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message=message,
    )


def log_deletion(request, obj, object_repr):
    """
    Log that an object will be deleted. Note that this method must be
    called before the deletion.

    """
    from django.contrib.admin.models import DELETION, LogEntry

    return LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=object_repr,
        action_flag=DELETION,
    )


def pretty_change_message(obj):
    """
    Takes in an object and returns a pretty version of its change message from its LogEntry object.
    """
    from django.contrib.admin.models import LogEntry

    query = LogEntry.objects.filter(
        content_type_id=get_content_type_for_model(obj).pk, object_id=obj.pk
    )
    if not query.exists():
        return "Wrong reference!"
    return str(query[0])


def daterange(start_date, end_date):
    """
    Generator function to do iteration over the range of dates given.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def safe_object_delete_log(request, model, pk: str | int) -> tuple:
    """
    Extension to safe_object_delete(), except that it logs the deletion of the object.
    """
    object_given = model.objects.get(pk=pk)
    log_deletion(request, object_given, str(object_given))
    return safe_object_delete(model, pk)
