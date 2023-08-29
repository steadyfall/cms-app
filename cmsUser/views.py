from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.db.models import Sum
from adminpanel.models import Plant, Case
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

from django.contrib import messages

from authorizer.models import Profile
from django.contrib.auth.models import User

# Useful constants and functions
PAGINATE_NO = 5


# Views


class MainPage(LoginRequiredMixin, View):
    def context_creator(self):
        user = User.objects.get(pk=self.request.user.pk)
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
        profile = Profile.objects.get(user=user)
        plant_name = (
            " (" + profile.assigned_plant.name + ")"
            if self.request.user.is_authenticated
            else ""
        )
        total_count = (
            profile.assigned_plant.all_cases.aggregate(total_count=Sum("count"))[
                "total_count"
            ]
            if self.request.user.is_authenticated
            else 0
        )
        context = dict(
            title=f"Plant Management{plant_name}",
            total_count=total_count,
            cases=profile.assigned_plant.all_cases.order_by("-count")[:7],
        )
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "cmsUser/mainpage.html", self.context_creator())


class ChangeRecord(LoginRequiredMixin, View):
    id_prefix_for_case_count_input = "case-"

    def context_creator(self):
        request_user = User.objects.get(pk=self.request.user.pk)
        user_profile = Profile.objects.get(user=request_user)

        def formIDQuery(identifier_string):
            return user_profile.assigned_plant.all_cases.annotate(
                form_id=Concat(
                    V(
                        f"{identifier_string}",
                    ),
                    "pk",
                    output_field=CharField(),
                ),
            )

        def formValidatorCodeGenerator(query):
            return "\n".join(
                list(
                    query.annotate(
                        form_cmd=Concat(
                            V(
                                f"$('#",
                            ),
                            "form_id",
                            V(
                                (
                                    """').on("input focus keyup click change", function () {\n"""
                                    """\tvar isValid = onlyNumber(this.value);\n"""
                                    """\tconsole.log(isValid);\n"""
                                    """\treturn inputValid(this, isValid);\n"""
                                    "});"
                                )
                            ),
                            output_field=CharField(),
                        )
                    )
                    .order_by("id")
                    .values_list("form_cmd", flat=True)
                )
            )

        plant_shortname = ""
        if self.request.user.is_authenticated:
            plant_shortname = " ("
            [
                plant_shortname := (lambda x: plant_shortname + x)(word[0])
                for word in user_profile.assigned_plant.name.split()
            ]
            plant_shortname += ")"
        total_count = (
            user_profile.assigned_plant.all_cases.aggregate(total_count=Sum("count"))[
                "total_count"
            ]
            if self.request.user.is_authenticated
            else 0
        )
        query_ready_for_form = formIDQuery(ChangeRecord.id_prefix_for_case_count_input)
        form_id_list = list(
            query_ready_for_form.order_by("id").values_list("form_id", flat=True)
        )
        form_id_commands = formValidatorCodeGenerator(query_ready_for_form)
        paginator = Paginator(query_ready_for_form.order_by("-amount"), PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = dict(
            title=f"Add Records{plant_shortname}",
            total_count_as_of_now=total_count,
            plant_shortname=plant_shortname,
            cases=objects_list,  # enumerate(query_ready_for_form.order_by("-amount"), start=1),
            form_id_commands=form_id_commands,
            form_id_list=form_id_list,
        )
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "cmsUser/updaterecords.html", self.context_creator())

    def post(self, request, *args, **kwargs):
        request_user = User.objects.get(pk=self.request.user.pk)
        user_profile = Profile.objects.get(user=request_user)
        cases = list(
            filter(
                lambda x: (ChangeRecord.id_prefix_for_case_count_input in x)
                and request.POST.get(x).strip().isdigit(),
                request.POST.keys(),
            )
        )
        # print(cases)
        if not cases:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        cases = list(
            map(lambda x: x.strip(ChangeRecord.id_prefix_for_case_count_input), cases)
        )
        if not all(map(lambda x: x.isdigit(), cases)):
            # print("Error: all(map(lambda x: x.isdigit(), cases))")
            messages.error(self.request, "Invalid data is trying to be updated.")
            return render(request, "cmsUser/updaterecords.html", self.context_creator())

        cases = list(map(lambda x: int(x), cases))
        if not all(
            map(
                lambda x: len(Case.objects.filter(pk=int(x))) == 1
                and (
                    Case.objects.filter(pk=int(x))[0].for_plant
                    == user_profile.assigned_plant
                ),
                cases,
            )
        ):
            # print("Error: len(Case.objects.filter(pk=int(x))) == 1")
            messages.error(
                self.request, "Non-existant/duplicate cases are trying to be updated."
            )
            return render(request, "cmsUser/updaterecords.html", self.context_creator())

        change_count = 0
        for case_id in cases:
            key = f"{ChangeRecord.id_prefix_for_case_count_input}{case_id}"
            value = int(request.POST.get(key))
            case_fromCaseId = Case.objects.get(pk=case_id)
            if case_fromCaseId.count == value:
                continue
            else:
                # print("HHHH")
                change_count += 1
                case_fromCaseId.count = value
                case_fromCaseId.save(update_fields=["count", "last_updated"])

        messages.success(
            self.request,
            f"Updated {change_count} record{'s' if change_count > 1 else ''}.",
        )
        return render(request, "cmsUser/updaterecords.html", self.context_creator())


class ViewRecords(View):
    def context_creator(self):
        request_user = User.objects.get(pk=self.request.user.pk)
        user_profile = Profile.objects.get(user=request_user)
        plant_name = (
            " (" + user_profile.assigned_plant.name + ")"
            if self.request.user.is_authenticated
            else ""
        )
        plant_shortname = ""
        if self.request.user.is_authenticated:
            plant_shortname = " ("
            [
                plant_shortname := (lambda x: plant_shortname + x)(word[0])
                for word in user_profile.assigned_plant.name.split()
            ]
            plant_shortname += ")"
        manager = user_profile.assigned_plant.all_cases
        total_count = (
            manager.aggregate(total_count=Sum("count"))["total_count"]
            if self.request.user.is_authenticated
            else 0
        )
        order = ""
        if self.request.GET.get("amt"):
            order += "-amount" if not order else " -amount"
        elif self.request.GET.get("count"):
            order += "-count" if not order else " -count"
        elif self.request.GET.get("updated"):
            order += "-last_updated" if not order else " -last_updated"
        elif self.request.GET.get("created"):
            order += "-date_created" if not order else " -date_created"
        order = "-count" if not order else order
        paginator = Paginator(manager.order_by(order), PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = dict(
            title=f"Plant Management{plant_name}",
            total_count_as_of_now=total_count,
            plant_shortname=plant_shortname,
            cases=objects_list,
        )
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "cmsUser/viewrecords.html", self.context_creator())
