from django.forms import ModelForm
from .models import Plant, Zone, Case
from django.contrib.auth.models import User


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
