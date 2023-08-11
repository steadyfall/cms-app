from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class MainPage(View):
    def get(self, request, *args, **kwargs):
        plant_name = (
            " (" + self.request.user.profile.assigned_plant.name + ")"
            if self.request.user.is_authenticated
            else ""
        )
        context = {"title": f"Plant Management{plant_name}"}
        return render(request, "cmsUser/mainpage.html", context)
