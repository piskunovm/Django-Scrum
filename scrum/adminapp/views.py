from django.conf import settings
from tzlocal import get_localzone
import pytz
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from adminapp.forms import AdminUserRegisterForm
from adminapp.helpers.search import perform_search_ajax
from authapp.models import User
from mainapp.helpers import get_current_user
from mainapp.helpers.article.article import get_category_list
from mainapp.helpers.search import perform_search


@login_required
def get_users(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    current_user = get_current_user(request)
    if current_user.user_role == "administrator":
        title = "Админка|Пользователи"
        content = {
            "title": title,
            'users': User.objects.all().order_by('pk'),
            "current_user": current_user,
        }
        return render(request, "adminapp/users_table_page.html", content)
    return HttpResponseRedirect(reverse("main:index"))


@login_required
def change_user_status(request, pk):
    current_user = get_current_user(request)
    if current_user.user_role == "administrator":
        user = User.objects.filter(pk=pk).first()
        if not (
                user.is_superuser or current_user.id == user.id or user.user_role == 'administrator' and not current_user.is_superuser):
            user.is_active = not user.is_active
        user.save()
        if request.is_ajax():
            user_is_active_status = user.is_active
            return JsonResponse({"user_is_active_status": user_is_active_status})
        return HttpResponseRedirect(reverse("adminapp:get_users"))
    return HttpResponseRedirect(reverse("main:index"))


def change_user_role(request, pk, role):
    user = User.objects.filter(pk=pk).first()
    user.user_role = role
    user.save()

    if request.is_ajax():
        content = {
            "user": user,
        }
        return JsonResponse({"user_role": user.user_role})

    return HttpResponseRedirect(reverse("adminapp:get_users"))


def create_user(request):
    if request.method == "POST":
        form = AdminUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("adminapp:get_users"))
    else:
        form = AdminUserRegisterForm()
    context = {
        "title": "Регистрация пользователя",
        "form": form,
        "categories": get_category_list,
    }

    return render(request, "adminapp/users_creation_page.html", context)


def get_user_info(request, pk):
    user = User.objects.filter(pk=pk).first()
    if request.is_ajax():
        return JsonResponse(
            {
                "user": {
                    "user_id": pk,
                    "user_status": user.is_active,
                    "user_role": user.user_role
                }
            }
        )
    return JsonResponse({"user": {"user_id": pk, "user_status": user.is_active, "user_role": user.user_role}})


def search_ajax(request):
    search_request = request.GET.get("search_request")
    search_filter = request.GET.get("filter")
    if request.is_ajax():
        search_output = perform_search_ajax(search_request, search_filter)
        return JsonResponse({"search_output": search_output})
    return HttpResponseRedirect(reverse("adminapp:get_users"))

