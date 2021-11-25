import os
from datetime import datetime
from tzlocal import get_localzone
import pytz
from django.utils import timezone

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from authapp.helpers import deactivate_user
from authapp.models import User
from authapp.views import logout
from lkapp.forms import UserProfileForm, PostCreationForm
from lkapp.helpers.alerts import get_alerts, get_mail_settings, set_mail_settings
from lkapp.helpers.alerts.alert import AlertFrontHandler, count_alerts
from lkapp.helpers.rating_author import get_rate_author
from lkapp.helpers.ban_of_user.ban import ban_is_active, get_ban_obj
from lkapp.helpers.ban_of_user.user_ban import FOREVER
from mainapp.helpers import get_current_user
from mainapp.helpers.article.article import get_category_list, get_article
from mainapp.helpers.scores.score_author import get_count_user_likes, get_count_user_dislikes
from mainapp.models import Article
from django.views.decorators.csrf import csrf_exempt
from mainapp.models import Complaint
from .helpers import (
    get_hash,
    hash_equality,
)
from .helpers.complains import (
    set_complain_status,
    get_complains_comments_on_moderation,
    get_complains_posts_on_moderation,
    get_complains_on_moderation,
)
from .helpers.posts.my_posts import (
    get_articles,
    get_articles_on_moderation,
    publicate_post,
    delete_draft,
    archivate_post,
    set_article_status,
)
from .models import Alert


@user_passes_test(lambda x: x.is_authenticated)
def my_profile(request, pk):
    timezone.activate(pytz.timezone(str(get_localzone())))
    if request.user.id != pk:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        title = "ЛК|Профиль"
        content = {
            "title": title,
            "user": get_current_user(request),
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
            "rate_author": get_rate_author(pk),
            "count_likes": get_count_user_likes(pk),
            "count_dislikes": get_count_user_dislikes(pk),
            "email_setting": get_mail_settings(request.user.id),
            "ban": ban_is_active(pk),
            "ban_info": get_ban_obj(pk),
        }

        if ban_is_active(pk):
            ban_obj = get_ban_obj(pk)
            create_time = ban_obj.created_at
            end_time = ban_obj.ban_end_time
            delta = end_time - create_time
            result = delta.days * 1440 + 639
            print(result)
            if result == FOREVER:
                content['ban_time'] = 'Бессрочный'
            else:
                content['ban_time'] = ban_obj.ban_end_time

    return render(request, "lkapp/profile.html", content)


@user_passes_test(lambda x: x.is_authenticated)
def profile_update(request, pk):
    user = get_object_or_404(User, pk=int(pk))
    if request.user.id != pk:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        if request.method == "POST":
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                return HttpResponseRedirect(
                    reverse(
                        "my_lk:my_profile",
                        kwargs={
                            "pk": user.id,
                        },
                    )
                )
        else:
            profile_form = UserProfileForm(instance=user)

    context = {
        "title": "пользователи/редактирование",
        "form": profile_form,
        "user": user,
        "categories": get_category_list,
        "alert": count_alerts(request),
    }

    return render(request, "lkapp/update_profile.html", context)


@user_passes_test(lambda x: x.is_authenticated)
def delete_user(request):
    deactivate_user(request)
    return logout(request)


def post_creation(request):
    user = get_current_user(request)
    title = "ЛК|Создание поста"

    if ban_is_active(request.user.id):
        return HttpResponseRedirect(reverse("lkapp:my_profile", kwargs={"pk": request.user.id}))
    else:
        if request.method == "POST":
            post_creation_form = PostCreationForm(request.POST, request.FILES)
            if post_creation_form.is_valid():
                new_post = Article()
                new_post.title = post_creation_form.cleaned_data["title"]
                new_post.preview = post_creation_form.cleaned_data["preview"]
                new_post.body = post_creation_form.cleaned_data["body"]
                new_post.image = post_creation_form.cleaned_data["image"]
                new_post.category = post_creation_form.cleaned_data["category"]
                new_post.tag = post_creation_form.cleaned_data["tag"]
                new_post.author = user
                new_post.save()
                # после сохранения черновика переход на страницу с черновиками
                return HttpResponseRedirect(reverse("lkapp:drafts"))
            else:
                print("INVALID")
        else:
            post_creation_form = PostCreationForm()

        content = {
            "title": title,
            "current_datetime": datetime.now(),
            "form": post_creation_form,
            "author": f"{user.first_name} {user.last_name}",
            "categories": get_category_list,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/create_post_page.html", content)


@login_required()
def my_posts(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Мои посты"
    content = {
        "title": title,
        "articles": get_articles(request, "-updated_at"),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
        "ban": ban_is_active(request.user.id),
        "ban_info": get_ban_obj(request.user.id),
    }
    return render(request, "lkapp/my_posts.html", content)


@login_required()
def my_subscribes(request):
    title = "Мои подписки"
    user = get_current_user(request)
    subscribes = user.follows.all()
    subscribers = user.followers.all()
    content = {
        "title": title,
        "user": user,
        "subscribes": subscribes,
        "subscribers": subscribers,
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/my_subscribes.html", content)


@login_required
def my_posts_ajax(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Мои посты"
    content = {
        "title": title,
        "articles": get_articles(request),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "ban": ban_is_active(request.user.id),
        "ban_info": get_ban_obj(request.user.id),
    }
    print(request)
    return render(request, "lkapp/includes/article_list.html", content)
    # return render(request, "lkapp/my_posts.html", content)


@login_required()
def posts_on_moderation(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Посты на модерации"
    content = {
        "title": title,
        "articles": get_articles_on_moderation(request, "-updated_at"),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/posts_on_moderation.html", content)


@login_required()
def my_drafts(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Мои черновики"
    content = {
        "title": title,
        "drafts": get_articles(request, "-updated_at"),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
        "ban": ban_is_active(request.user.id),
        "ban_info": get_ban_obj(request.user.id),
    }
    return render(request, "lkapp/my_drafts.html", content)


@login_required()
def preview_draft(request, pk):
    if request.user.id != get_article(pk).author_id:
        title = "Ошибка доступа"
        content = {
            "title": title,
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
        }
        return render(request, "lkapp/errors/access_error.html", content)
    else:
        article = get_article(pk, status="draft")
        title = f"Черновик - {article.title}"
        content = {
            "title": title,
            "article": article,
            "user": get_current_user(request),
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/preview_draft.html", content)


@login_required()
def preview_post(request, pk):
    if request.user.id != get_article(pk).author_id:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        article = get_article(pk)
        title = f"{article.title}"
        content = {
            "title": title,
            "article": article,
            "user": get_current_user(request),
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
            "audio_url": os.path.join("\\media\\article_audio", article.audio_name),
        }
        return render(request, "lkapp/preview_post.html", content)


@user_passes_test(lambda x: x.is_authenticated)
def publicating_post(request, pk):
    post_status = get_article(pk).status
    user_ban = ban_is_active(request.user.id)
    if user_ban:
        return HttpResponseRedirect(reverse("lkapp:my_profile", kwargs={"pk": request.user.id}))
    else:
        if request.user.id != get_article(pk).author_id:
            return HttpResponseRedirect(reverse("authapp:login"))
        else:
            if post_status != "draft" and post_status != "correction":
                return HttpResponseRedirect(reverse("lkapp:my_posts"))
            else:
                publicate_post(request, pk, post_status)
                return HttpResponseRedirect(reverse("lkapp:my_posts"))


@user_passes_test(lambda x: x.is_authenticated)
def approve_post(request, pk):
    approve_post(request, pk)
    return HttpResponseRedirect(reverse("lkapp:mypost", kwargs={"pk": pk}))


@user_passes_test(lambda x: x.is_authenticated)
def reject_post(request, pk):
    reject_post(request, pk)
    return HttpResponseRedirect(reverse("lkapp:mypost", kwargs={"pk": pk}))


@user_passes_test(lambda x: x.is_authenticated)
def archivating_post(request, pk):
    if request.user.id != get_article(pk).author_id:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        if get_article(pk).status != "published":
            title = "Ошибка доступа"
            content = {
                "title": title,
                "categories": get_category_list,
                "media_url": settings.MEDIA_URL,
            }
            return render(request, "lkapp/errors/status_error.html", content)
        else:
            archivate_post(request, pk)
            return HttpResponseRedirect(reverse("lkapp:my_posts"))


@user_passes_test(lambda x: x.is_authenticated)
def delete_drafts(request, pk):
    if request.user.id != get_article(pk).author_id:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        delete_draft(request, pk)
        return HttpResponseRedirect(reverse("lkapp:drafts"))


@login_required()
def post_moderation(request, pk):
    user = User.objects.filter(pk=request.user.id).first()
    if user.user_role in ("moderator", "administrator"):
        title = "Предварительный просмотр статьи"
        content = {
            "title": title,
            "article": get_article(pk, status="moderation"),
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/post_moderation.html", content)
    else:
        title = "Ошибка доступа"
        content = {
            "title": title,
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/errors/access_error.html", content)


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_article_status_correction(request, pk):
    return set_article_status(request, pk, "correcting")


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_article_status_published(request, pk):
    return set_article_status(request, pk, "moderated")


@login_required()
def edit_post(request, pk):
    user_ban = ban_is_active(request.user.id)
    if user_ban:
        return HttpResponseRedirect(reverse("lkapp:my_profile", kwargs={"pk": request.user.id}))
    else:
        if request.user.id != get_article(pk).author_id:
            return HttpResponseRedirect(reverse("authapp:login"))
        else:
            title = "Редактирование поста"
            post = get_object_or_404(Article, pk=pk)
            post_status = post.status
            # получаем хэш от данных, которые были в форме
            hash_sum_1 = get_hash(post)
            if post_status != "correction" and post_status != "published":
                return HttpResponseRedirect(reverse("lkapp:my_posts"))
            if request.method == "POST":
                edit_form = PostCreationForm(request.POST, request.FILES, instance=post)
                if edit_form.is_valid():
                    # получаем хэш от данных, которые есть на момент нажатия кнопки сохранить
                    hash_sum_2 = get_hash(post)
                    # если хэши разные - сохраняем и меняем статус
                    if not hash_equality(hash_sum_1, hash_sum_2):
                        edit_form.save()
                        # сохранили данные и перешли на страницу мои хабы. Поменяли статус "На модерации"
                        publicate_post(request, pk, post_status)
                    return HttpResponseRedirect(reverse("lkapp:my_posts"))
                else:
                    return HttpResponseRedirect(
                        reverse(
                            "my_lk:edit_post",
                            kwargs={
                                "pk": post.id,
                            },
                        )
                    )
            else:
                edit_form = PostCreationForm(instance=post)

        content = {
            "title": title,
            "media_url": settings.MEDIA_URL,
            "categories": get_category_list,
            "form": edit_form,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/edit_post.html", content)


@login_required()
def edit_draft(request, pk):
    if request.user.id != get_article(pk).author_id:
        return HttpResponseRedirect(reverse("authapp:login"))
    else:
        title = "Редактирование черновика"
        post = get_object_or_404(Article, pk=pk)
        # обработка случая, если адрес с № статьи забит в адресную строку
        # получаем статус статьи. Если moderation, то возвращаем страницу со статьями на модерации
        # тк статьи с данным статусом нельзя редактировать
        post_status = post.status
        # получаем хэш от данных, которые были в форме
        hash_sum_1 = get_hash(post)
        if post_status != "draft":
            return HttpResponseRedirect(reverse("lkapp:drafts"))
        if request.method == "POST":
            edit_form = PostCreationForm(request.POST, request.FILES, instance=post)
            if edit_form.is_valid():
                # получаем хэш от данных, которые есть на момент нажатия кнопки сохранить
                hash_sum_2 = get_hash(post)
                # если хэши разные - сохраняем
                if not hash_equality(hash_sum_1, hash_sum_2):
                    edit_form.save()
                # сохранили данные и перешли на страницу черновиков
                return HttpResponseRedirect(reverse("lkapp:drafts"))
            else:
                return HttpResponseRedirect(
                    reverse(
                        "my_lk:edit_draft",
                        kwargs={
                            "pk": post.id,
                        },
                    )
                )
        else:
            edit_form = PostCreationForm(instance=post)

    content = {
        "title": title,
        "media_url": settings.MEDIA_URL,
        "categories": get_category_list,
        "form": edit_form,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/edit_draft.html", content)


@login_required()
def my_alerts(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Мои уведомления"
    content = {
        "title": title,
        "categories": get_category_list(),
        "alerts": AlertFrontHandler(get_alerts(request)),
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/my_alerts.html", content)


@login_required()
def my_alerts_ajax(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Мои уведомления"
    content = {
        "title": title,
        "categories": get_category_list(),
        "alerts": AlertFrontHandler(get_alerts(request)),
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/includes/alert_list.html", content)


@login_required()
def delete_all_alerts(request):
    """Удаляет все события"""
    try:
        Alert.objects.filter(alert_user_id=request.user.id).delete()
    except Exception:
        pass
    return HttpResponseRedirect(reverse("lkapp:my_alerts"))


@login_required()
def delete_read_alerts(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    """Удаляет прочитанные события"""
    try:
        Alert.objects.filter(alert_user_id=request.user.id, not_read=0).delete()
    except Exception:
        pass
    return HttpResponseRedirect(reverse("lkapp:my_alerts"))


@csrf_exempt
@login_required()
def delete_alert(request, pk):
    timezone.activate(pytz.timezone(str(get_localzone())))
    """Удаляет отдельное уведомление"""
    try:
        Alert.objects.filter(id=pk).delete()
    except Exception:
        pass
    if request.is_ajax():
        title = "Мои уведомления"
        if request.method == "POST":
            url_ajax = request.POST.get("type_post")
        content = {
            "title": title,
            "categories": get_category_list(),
            "alerts": AlertFrontHandler(get_alerts(request, url_ajax)),
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/includes/alert_list.html", content)
    return HttpResponseRedirect(reverse("lkapp:my_alerts"))


@csrf_exempt
@login_required()
def mark_as_read(request, pk):
    timezone.activate(pytz.timezone(str(get_localzone())))
    """Помечает событие, как прочитанное"""
    try:
        Alert.objects.filter(id=pk).update(not_read=0)
    except Exception:
        pass
    if request.is_ajax():
        title = "Мои уведомления"
        if request.method == "POST":
            url_ajax = request.POST.get("type_post")
        content = {
            "title": title,
            "categories": get_category_list(),
            "alerts": AlertFrontHandler(get_alerts(request, url_ajax)),
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/includes/alert_list.html", content)
    else:
        return HttpResponseRedirect(reverse("lkapp:my_alerts"))


@login_required()
def my_complains(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Жалобы на модерации"
    content = {
        "title": title,
        "complains": get_complains_on_moderation(request),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/my_complains.html", content)


@login_required()
def my_complains_ajax(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Жалобы на модерации"
    content = {
        "title": title,
        "complains": get_complains_on_moderation(request),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
    }
    print(request)
    return render(request, "lkapp/includes/complain_list.html", content)


@login_required()
def my_complains_post_ajax(request):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "Жалобы на модерации"

    content = {
        "title": title,
        "complains": get_complains_posts_on_moderation(request),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
    }
    print(request)
    return render(request, "lkapp/includes/complain_list.html", content)


@login_required()
def my_complains_comments_ajax(request):
    title = "Жалобы на модерации"

    content = {
        "title": title,
        "complains": get_complains_comments_on_moderation(request),
        "categories": get_category_list,
        "media_url": settings.MEDIA_URL,
    }
    print(request)
    return render(request, "lkapp/includes/complain_list.html", content)


@login_required()
def complain_moderation(request, pk):
    user = User.objects.filter(pk=request.user.id).first()
    if user.user_role in ("moderator", "administrator"):
        title = "Предварительный просмотр статьи"
        complain = Complaint.objects.get(pk=pk, status="active")
        content = {
            "title": title,
            "complain": complain,
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/complain_moderation.html", content)
    else:
        title = "Ошибка доступа"
        content = {
            "title": title,
            "categories": get_category_list,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
        }
        return render(request, "lkapp/errors/access_error.html", content)


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_complain_status_approve(request, pk):
    return set_complain_status(request, pk, "approve")


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_complain_status_denied(request, pk):
    return set_complain_status(request, pk, "moderated")


def set_mail_settting_switcher(request, pk):
    set_mail_settings(request.user.id)
    if request.is_ajax():
        return JsonResponse({"check": True})
    else:
        return HttpResponseRedirect(reverse("my_lk:my_profile", kwargs={"pk": pk}))


def get_mail_settting_switcher(request):
    return get_mail_settings(request.user.id)


# Сигналы для уведомлений (старая версия)
# @receiver(post_save, sender=Article)
# @receiver(post_save, sender=Comments)
# @receiver(post_save, sender=Dislike)
# @receiver(post_save, sender=Like)
# def filling_alert_table(sender, instance, created, **kwargs):
#     if sender.__name__ == "Article":
#         author_id = instance.author_id
#         article_id = instance.id
#         action_user_id = instance.moderator_id
#
#         if str(instance.status) == "published":
#             event_description = "Статья опубликована"
#
#         elif str(instance.status) == "correction":
#             event_description = "Статья отклонена"
#         else:
#             pass
#
#     if sender.__name__ == "Like":
#         try:
#             event_description = "Лайк"
#             action_user_id = instance.user.id
#             author_id = instance.article.author.id
#             article_id = instance.article.id
#         except AttributeError:
#             pass
#
#     if sender.__name__ == "Dislike":
#         try:
#             event_description = "Дизлайк"
#             author_id = instance.article.author.id
#             article_id = instance.article.id
#             action_user_id = instance.user.id
#             # article_title = instance.article.title
#         except AttributeError:
#             pass
#
#     if sender.__name__ == "Comments":
#         try:
#             event_description = "Комментарий"
#             action_user_id = instance.author_comment.id
#             author_id = instance.article.author.id
#             article_id = instance.article.id
#             # article_title = instance.article.title
#         except AttributeError:
#             pass
#
#     try:
#         Alert.objects.create(
#             basic_user_id=author_id,
#             article_link_id=article_id,
#             performed_action_user_id=action_user_id,
#             event=event_description,
#         )
#
#     except Exception:
#         pass
#
