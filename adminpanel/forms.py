from django.forms import ModelForm, fields, ValidationError
from .models import Plant, Zone, Case
from django.contrib.auth.models import User
from authorizer.models import Profile
from django.contrib.auth import password_validation
from copy import deepcopy


class ModifiedModelForm(ModelForm):
    _newly_created: bool

    def __init__(self, *args, **kwargs):
        self._newly_created = kwargs.get("instance") is None
        super().__init__(*args, **kwargs)


class PlantForm(ModelForm):
    template_name = "formTemplates/plant.html"

    class Meta:
        model = Plant
        fields = [
            "zone",
            "name",
        ]
        exclude = ["date_created"]


class ZoneForm(ModelForm):
    template_name = "formTemplates/zone.html"

    class Meta:
        model = Zone
        fields = [
            "location",
        ]
        exclude = ["date_created"]


class CaseForm(ModelForm):
    template_name = "formTemplates/case.html"

    class Meta:
        model = Case
        fields = [
            "amount",
            "count",
            "for_plant",
        ]
        exclude = ["date_created", "last_updated"]


class UserChangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._newly_created = kwargs.get("instance") is None
        super().__init__(*args, **kwargs)

    template_name = "formTemplates/user.html"

    newPassword = fields.CharField(
        min_length=8, max_length=128, strip=True, required=False
    )
    confirmNewPassword = fields.CharField(
        min_length=8, max_length=128, strip=True, required=False
    )
    changePassword = fields.BooleanField(required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_newPassword(self):
        newPassword = self.cleaned_data.get("newPassword")
        if not newPassword:
            return newPassword
        try:
            password_validation.validate_password(newPassword, self.instance)
        except ValidationError as error:
            self.add_error("newPassword", error)
        return newPassword

    def clean_confirmNewPassword(self):
        confirmNewPassword = self.cleaned_data.get("confirmNewPassword")
        if not confirmNewPassword:
            return confirmNewPassword
        try:
            password_validation.validate_password(confirmNewPassword, self.instance)
        except ValidationError as error:
            self.add_error("confirmNewPassword", error)
        if self.cleaned_data.get("newPassword") != confirmNewPassword:
            self.add_error("confirmNewPassword", "Passwords are not identical.")
        return confirmNewPassword

    def save(self, commit=True, *args, **kwargs):
        if not commit:
            raise NotImplementedError(
                "Need to accomodate for fields unique to User model."
            )
        model = self._meta.model
        if self._newly_created:
            new_cleaned_data = deepcopy(self.cleaned_data)
            pwd = deepcopy(new_cleaned_data["newPassword"])
            del new_cleaned_data["confirmNewPassword"]
            del new_cleaned_data["changePassword"]
            del new_cleaned_data["newPassword"]
            objectInstance = model.objects.create(**new_cleaned_data)
            objectInstance.set_password(pwd)
            objectInstance.save()
            Profile.objects.create(user=objectInstance)
            return objectInstance
        else:
            objectInstance = self.instance
            if self.has_changed:
                changed_fields = list(self.changed_data)
                if (
                    self.cleaned_data["changePassword"]
                    and self.cleaned_data["newPassword"]
                    and self.cleaned_data["confirmNewPassword"]
                    and (
                        self.cleaned_data["newPassword"]
                        == self.cleaned_data["confirmNewPassword"]
                    )
                ):
                    objectInstance.set_password(self.cleaned_data["newPassword"])
                    objectInstance.save()
                if "changePassword" in changed_fields:
                    changed_fields.remove("changePassword")
                if "newPassword" in changed_fields:
                    changed_fields.remove("newPassword")
                if "confirmNewPassword" in changed_fields:
                    changed_fields.remove("confirmNewPassword")
                differenceBetweenFields = [self.cleaned_data[x] for x in changed_fields]
                for idx in range(len(changed_fields)):
                    field = changed_fields[idx]
                    newData = differenceBetweenFields[idx]
                    setattr(objectInstance, field, newData)
                objectInstance.save()
            return objectInstance


class ProfileForm(ModelForm):
    template_name = "formTemplates/profile.html"

    class Meta:
        model = Profile
        fields = [
            "assigned_plant",
        ]
        exclude = ["user"]
