from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.db.models import Sum
from adminpanel.models import Plant, Case
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat


class MainPage(View):
    def context_creator(self):
        plant_name = (
            " (" + self.request.user.profile.assigned_plant.name + ")"
            if self.request.user.is_authenticated
            else ""
        )
        total_count = (
            self.request.user.profile.assigned_plant.all_cases.aggregate(
                total_count=Sum("count")
            )["total_count"]
            if self.request.user.is_authenticated
            else 0
        )
        context = dict(
            title=f"Plant Management{plant_name}",
            total_count=total_count,
            cases=self.request.user.profile.assigned_plant.all_cases.order_by("-count"),
        )
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "cmsUser/mainpage.html", self.context_creator())

