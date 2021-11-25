from datetime import datetime

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from authapp.forms import UserLoginForm, UserRegisterForm
from mainapp.helpers.article.article import get_category_list
from mainapp.models import UserBan


def login(request):
    title = "вход"
    redirect_to = request.GET.get('next')
    login_form = UserLoginForm(data=request.POST or None)
    if request.method == "POST" and login_form.is_valid():
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if redirect_to:
                return HttpResponseRedirect(redirect_to)
            else:
                return HttpResponseRedirect(request.POST["returnurl"])

# передаем на страницу название, форму регистрации и категории хабов для отображения в меню
    content = {
        "title": title,
        "login_form": login_form,
        "categories": get_category_list,
        "referer_log": request.META.get('HTTP_REFERER'),
    }
    return render(request, "authapp/login.html", content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("main:index"))


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            new_user = auth.authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )

            auth.login(request, new_user)
            return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserRegisterForm()
    context = {
        "title": "Регистрация пользователя",
        "form": form,
        "categories": get_category_list,
    }
    if request.user.is_authenticated:
        return HttpResponseRedirect(
            reverse(
                "my_lk:my_profile",
                kwargs={
                    "pk": request.user.id,
                },
            )
        )
    else:
        return render(request, "authapp/registration.html", context)


def delete(request):
    confirmed = request.GET["confirmed"]
    user = request.user
    if confirmed == "true":
        user.delete()
        auth.logout(request)
        return HttpResponseRedirect(reverse("main:index"))
    else:
        return HttpResponseRedirect(
            reverse(
                "my_lk:profile_update",
                kwargs={
                    "pk": user.pk,
                },
            )
        )
