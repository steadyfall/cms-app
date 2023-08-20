from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from .models import Zone, Plant, Case
from authorizer.models import Profile

from .forms import PlantForm, CaseForm, ZoneForm, UserChangeForm, ProfileForm
from django.forms import ModelForm

from .mixins import SuperuserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.utils import construct_change_message

from .viewsExtra import (
    pk_checker,
    safe_pk_list_converter,
    safe_object_delete_log,
    pretty_change_message,
    log_addition,
    log_change,
    log_deletion,
    daterange,
    get_content_type_for_model,
)

# Useful constants

modelDict: dict[str, models.Model] = {
    "zone": Zone,
    "case": Case,
    "plant": Plant,
    "user": User,
}
allowedModelNames = tuple(modelDict.keys())
modelFormDict: dict[str, ModelForm] = {
    "zone": ZoneForm,
    "case": CaseForm,
    "plant": PlantForm,
    "user": UserChangeForm,
    "profile": ProfileForm,
}
addressOfPages = dict(
    adminMainPage=reverse_lazy("adminMainPage"),
    test=reverse_lazy("test"),
    adminListDB=lambda x: reverse_lazy("adminListDB", kwargs=x),
    adminListLogs=reverse_lazy("adminListLogs"),
    adminDBObject=lambda x: reverse_lazy("adminDBObject", kwargs=x),
    adminDBObjectCreate=lambda x: reverse_lazy("adminDBObjectCreate", kwargs=x),
    adminDBObjectDelete=lambda x: reverse_lazy("adminDBObjectDelete", kwargs=x),
    adminDBObjectHistory=lambda x: reverse_lazy("adminDBObjectHistory", kwargs=x),
)

PAGINATE_NO = 10
SITE_NAME = "AdminPanel"


# Test sites


def test(request):
    return render(request, "auth/signin.html")


# Actual production sites


class AdminListDB(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "admin-signin"
    raise_exception = True

    def get_url_kwargs(self):
        db = str(self.kwargs["db"])
        return db

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        query = (
            model.objects.all()
            .annotate(key_primary=F(model._meta.pk.name))
            .order_by("-key_primary")
        )
        if model is User:
            query = query.filter(is_staff=False).order_by("-key_primary")
        paginator = Paginator(query, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = {
            "allRecords": objects_list,
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - " + context["recordVerboseName"]
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title()],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if (
            smallcaseDB not in allowedModelNames
            or request.POST.get("admin-action") == "-"
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))

        model = modelDict[smallcaseDB]
        query = model.objects.all().annotate(key_primary=F(model._meta.pk.name))
        given_pk = request.POST.getlist("indcheck")
        safe_given_pk = safe_pk_list_converter(given_pk, model)
        if (
            request.POST.get("admin-action") == "Delete selected"
            and given_pk
            and (set(safe_given_pk) - set(map(lambda y: y.key_primary, query)) == set())
        ) or (
            request.POST.get("admin-action") == "Delete all in view"
            and request.POST.get("allcheck")
            and given_pk
            and (set(safe_given_pk) - set(map(lambda y: y.key_primary, query)) == set())
            and len(set(safe_given_pk)) == PAGINATE_NO
        ):
            object_name = (
                model._meta.verbose_name
                if len(given_pk) == 1
                else model._meta.verbose_name_plural
            )
            action = list(
                map(lambda x: safe_object_delete_log(request, model, x), safe_given_pk)
            )
            deleted = sum(list(map(lambda x: x[0], action)))
            messages.success(
                request,
                f"""Successfully deleted {len(action)} {object_name} and {deleted} objects related to it!""",
            )

        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)


class AdminDBObjectChange(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "admin-signin"
    raise_exception = True
    form_class = None
    instance = None

    def get_updatedAllowedModelNames(self):
        return tuple(list(allowedModelNames) + ["profile"])

    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def get_instance(self):
        """Return the initial data to use for forms on this view."""
        return AdminDBObjectChange.instance

    def get_form_class(self):
        """Return the form class to use."""
        return AdminDBObjectCreate.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "instance": self.get_instance(),
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = (
            modelDict[smallcaseDB]
            if smallcaseDB in allowedModelNames and smallcaseDB != "profile"
            else Profile
        )
        context = {
            "form": self.get_form(),
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - View " + context["recordVerboseName"].title()
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"View {smallcaseDB.title()}",
                addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in self.get_updatedAllowedModelNames():
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = (
            modelDict[smallcaseDB]
            if smallcaseDB in allowedModelNames and smallcaseDB != "profile"
            else Profile
        )
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])
        setattr(
            AdminDBObjectChange,
            "instance",
            model.objects.get(pk=int(pk) if pk.isnumeric() else pk),
        )
        context = self.context_creator()
        return render(request, "adminpanel/objectView.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in self.get_updatedAllowedModelNames():
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = (
            modelDict[smallcaseDB]
            if smallcaseDB in allowedModelNames and smallcaseDB != "profile"
            else Profile
        )
        setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])
        setattr(
            AdminDBObjectChange,
            "instance",
            model.objects.get(pk=int(pk) if pk.isnumeric() else pk),
        )
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)

        if request.POST.get("cancel"):
            return redirect("adminListDB", db=smallcaseDB)

        form = self.get_form()
        if not form.is_valid():
            # messages.warning(request, "Kindly check your input before submitting.")
            context = self.context_creator()
            return render(request, "adminpanel/objectView.html", context)

        if (request.POST.get("save") or request.POST.get("save_continue")) and (
            len(form.changed_data) != 0
        ):
            print(form.changed_data)
            saved_object = form.save(commit=True)
            change_message = construct_change_message(form, None, False)
            log_change(request, saved_object, change_message)
            pretty_msg = pretty_change_message(saved_object)
            messages.success(request, pretty_msg)
        if request.POST.get("save"):
            return redirect("adminDBList", db=smallcaseDB)
        elif request.POST.get("save_continue"):
            return redirect("adminDBObject", db=smallcaseDB, pk=pk)

        if request.POST.get("delete"):
            if smallcaseDB not in ("profile", "user"):
                return redirect("adminDBObjectDelete", db=smallcaseDB, pk=pk)

        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectCreate(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "admin-signin"
    raise_exception = True
    form_class = None
    initial = {}

    def get_url_kwargs(self):
        db = str(self.kwargs["db"])
        return db

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_form_class(self):
        """Return the form class to use."""
        return AdminDBObjectCreate.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "initial": self.get_initial(),
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        context = {
            "form": self.get_form(),
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = (
            SITE_NAME + " - Create " + context["recordVerboseName"].title()
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"Create {smallcaseDB.title()}",
                addressOfPages["adminDBObjectCreate"]({"db": smallcaseDB}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in ("profile",):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])
        context = self.context_creator()
        return render(request, "adminpanel/objectCreate.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in ("profile",):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        if request.POST.get("cancel"):
            return redirect("adminListDB", db=smallcaseDB)
        form = self.get_form()
        if not form.is_valid():
            context = self.context_creator()
            return render(request, "adminpanel/objectCreate.html", context)
        if request.POST.get("create"):
            new_object = form.save()
            change_message = construct_change_message(form, None, "add")
            log_addition(request, new_object, change_message)
            messages.success(request, pretty_change_message(new_object))
            return redirect("adminDBObject", db=smallcaseDB, pk=new_object.pk)
        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectDelete(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "admin-signin"
    raise_exception = True
    form_class = None
    instance = None

    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        obj = model.objects.get(pk=pk)
        context = {
            "record": obj,
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = (
            SITE_NAME + " - Confirm deleting " + context["recordVerboseName"] + "?"
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"View {smallcaseDB.title()}",
                addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
            ],
            [
                f"Delete '{obj}'",
                addressOfPages["adminDBObjectDelete"]({"db": smallcaseDB, "pk": pk}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "profile",
            "user",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        context = self.context_creator()
        return render(request, "adminpanel/objectDelete.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "profile",
            "user",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        if request.POST.get("yes") and not request.POST.get("no"):
            object_given = model.objects.get(pk=pk)
            object_name = object_given._meta.verbose_name
            log_deletion(request, object_given, str(object_given))
            pretty_msg = pretty_change_message(object_given)
            deleted = object_given.delete()[0]
            messages.success(
                request,
                pretty_msg
                + f"""\nSuccessfully deleted 1 {object_name} and {deleted} objects related to it!""",
            )
        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectHistory(View):
    pass


class ShowLogDB(View):
    pass
