import os
import time
from tzlocal import get_localzone
import pytz
from django.utils import timezone

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from authapp.models import User
from lkapp.helpers.alerts.alert import SaveAlert, count_alerts
from lkapp.helpers.ban_of_user.ban import ban_is_active, get_ban_obj
from lkapp.helpers.ban_of_user.user_ban import set_user_ban, set_user_unban
from scrum.settings import FOREVER
from lkapp.helpers.follow import check_follow
from lkapp.helpers.rating_author import get_rate_author
from .forms import Add_Comment_Form
from .helpers import (
    get_current_user,
    get_comment_for_complaint,
    get_user,
    get_count_post_likes,
    get_count_post_dislikes,
)
from .helpers.article.article import (
    get_article,
    get_category_list,
    get_articles,
    get_list_of_sorting_criteria_for_articles,
    get_count_published_posts,
)
from .helpers.article.article_audio import generate_article_audio
from .helpers.scores.score_author import (
    get_count_user_likes,
    check_user_liked,
    check_user_disliked,
    to_score,
    get_count_user_dislikes,
)
from .helpers.scores.score_comment import to_score_comment, read_comment_like, read_comment_dislike
from .helpers.scores.score_post import to_score_post, check_post_disliked, check_post_liked
from .helpers.search import perform_search
from .models import Article, Category, Complaint, Comments

from mainapp.helpers import get_comment


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_user_ban_status(request):
    return set_user_ban(request)


@user_passes_test(lambda x: x.is_authenticated and x.user_role in ("moderator", "administrator"))
def set_user_unban_status(request, pk):
    return set_user_unban(pk)


def profile_page(request, pk):
    title = "Страница автора"
    # Блок работы с часовыми поясами https://djangodoc.ru/3.2/topics/i18n/timezones/
    # получаем название часового пояса и устанавливаем его
    timezone.activate(pytz.timezone(str(get_localzone())))
    user = get_current_user(request)
    posts = Article.objects.filter(author=pk, status="published").order_by("-created_at")
    author_user = User.objects.get(id=pk)

    if user.is_authenticated:
        author_liked = check_user_liked(user, author_user)
        author_disliked = check_user_disliked(user, author_user)
    else:
        author_liked = False
        author_disliked = False

    content = {
        "title": title,
        "posts": posts,
        "user": user,
        # "user_auth": user_auth,
        "author_user": author_user,
        "categories": get_category_list(),
        "subscribers": author_user.followers.count(),
        "count_of_posts": get_count_published_posts(author_user.id),
        "button_to_stop_following": check_follow(request, pk),
        # возвращает значение для кнопки отмены подписки, True - если пользователь подписан
        "author_liked": author_liked,
        # необходимо для выбора цвета иконки лайка
        "author_disliked": author_disliked,
        # необходимо для выбора цвета иконки дизлайка
        "alert": count_alerts(request),
        "rate_author": get_rate_author(pk),
        "count_likes": get_count_user_likes(pk),
        "count_dislike": get_count_user_dislikes(pk),
        # проверяем того, на чью страницу зашли
        "ban": ban_is_active(pk),
        "ban_info": get_ban_obj(pk),
    }

    if ban_is_active(pk):
        ban_obj = get_ban_obj(pk)
        create_time = ban_obj.created_at
        end_time = ban_obj.ban_end_time
        delta = end_time - create_time
        result = delta.days * 1440 + 639
        if result == FOREVER:
            content['ban_time'] = 'Бессрочный'
        else:
            content['ban_time'] = ban_obj.ban_end_time

    return render(request, "mainapp/author_page.html", content)


@login_required
def follow(request, pk):
    timezone.activate(pytz.timezone(str(get_localzone())))
    author_user = User.objects.get(id=pk)
    user = get_current_user(request)
    if user == author_user:
        return HttpResponseRedirect(reverse("mainapp:profile_page", kwargs={"pk": pk}))
    else:
        if check_follow(request, pk):
            user.follows.remove(author_user)
            author_user.followers.remove(user)
            SaveAlert(action_user=request.user, alert_user=author_user, event_type="author_unsubscribe")
        else:
            user.follows.add(author_user)
            author_user.followers.add(user)
            SaveAlert(action_user=request.user, alert_user=author_user, event_type="author_subscribe")
        user.save()
        author_user.save()
        return HttpResponseRedirect(reverse("mainapp:profile_page", kwargs={"pk": pk}))


# Представление для рендера страницы статьи.
def read_post(request, pk=None, template="mainapp/article.html"):
    timezone.activate(pytz.timezone(str(get_localzone())))
    user = request.user
    article = get_article(pk)
    if article.status != "published" and article.status != "archive":
        return HttpResponseRedirect(reverse("main:index"))
    else:
        if user.is_authenticated:
            author_liked = check_post_liked(user, pk)
            author_disliked = check_post_disliked(user, pk)
        else:
            author_liked = False
            author_disliked = False

        title = "Чтение статьи"
        comments = article.comment.filter(main_parent__isnull=True)
        page = request.GET.get("page", 1)
        paginator = Paginator(comments, 10)

        try:
            comment = paginator.page(page)
        except PageNotAnInteger:
            comment = paginator.page(1)
        except EmptyPage:
            comment = paginator.page(paginator.num_pages)

        comment_form = Add_Comment_Form()

        content = {
            "title": title,
            "post": get_article(pk),
            "categories": get_category_list,
            "all_comments": comment,
            "comment_form": comment_form,
            "media_url": settings.MEDIA_URL,
            "alert": count_alerts(request),
            "author_liked": author_liked,
            "author_disliked": author_disliked,
            "like_count": get_count_post_likes(pk),
            "dislike_count": get_count_post_dislikes(pk),
            "like_comment": read_comment_like(request, pk),
            "dislike_comment": read_comment_dislike(request, pk),
            "audio_url": os.path.join("\\media\\article_audio", article.audio_name),
            "ban": ban_is_active(user.id),
            "ban_info": get_ban_obj(user.id),
        }
        return render(request, template, content)


def allert_counter(request):
    alert_count = count_alerts(request)
    response = {"count_alerts": alert_count}
    return JsonResponse(response)


@login_required
def like_author(request, pk):
    user = get_current_user(request)
    author_user = get_user(pk)
    if user == author_user:
        response = {
            "like_user_count": get_count_user_likes(author_user.id),
            "dislike_user_count": get_count_user_dislikes(author_user.id),
            "author_liked": False,
            "author_disliked": False,
        }
        return JsonResponse(response)
    else:
        print(
            f'Проверка лайков - {check_user_liked(user, author_user)}; Проверка дизлайков - {check_user_disliked(user, author_user)}')
        to_score(user, author_user, "like")
        print(
            f'Проверка лайков - {check_user_liked(user, author_user)}; Проверка дизлайков - {check_user_disliked(user, author_user)}')
        response = {
            "like_user_count": get_count_user_likes(author_user.id),
            "dislike_user_count": get_count_user_dislikes(author_user.id),
            "author_liked": check_user_liked(user, author_user),
            "author_disliked": check_user_disliked(user, author_user),
        }
        return JsonResponse(response)


@login_required
def dislike_author(request, pk):
    user = get_current_user(request)
    author_user = get_user(pk)
    if user == author_user:
        response = {
            "like_user_count": get_count_user_likes(author_user.id),
            "dislike_user_count": get_count_user_dislikes(author_user.id),
            "author_liked": False,
            "author_disliked": False,
        }
        return JsonResponse(response)
    else:
        print(
            f'Проверка лайков - {check_user_liked(user, author_user)}; Проверка дизлайков - {check_user_disliked(user, author_user)}')
        to_score(user, author_user, "dislike")
        print(
            f'Проверка лайков - {check_user_liked(user, author_user)}; Проверка дизлайков - {check_user_disliked(user, author_user)}')
        response = {
            "like_user_count": get_count_user_likes(author_user.id),
            "dislike_user_count": get_count_user_dislikes(author_user.id),
            "author_liked": check_user_liked(user, author_user),
            "author_disliked": check_user_disliked(user, author_user),
        }
        return JsonResponse(response)


def like_post(request, pk=None):
    user = get_current_user(request)
    article = get_article(pk)
    if user.id == article.author_id:
        response = {
            "like_count": get_count_post_likes(pk),
            "dislike_count": get_count_post_dislikes(pk),
            "author_liked": False,
            "author_disliked": False,
            "rating_count": article.rating,
        }
        return JsonResponse(response)
    else:
        to_score_post(user, pk, "like")
        article = get_article(pk)

        response = {
            "like_count": get_count_post_likes(pk),
            "dislike_count": get_count_post_dislikes(pk),
            "author_liked": check_post_liked(user, pk),
            "author_disliked": check_post_disliked(user, pk),
            "rating_count": article.rating,
        }
        return JsonResponse(response)


def dislike_post(request, pk=None):
    user = get_current_user(request)
    article = get_article(pk)
    if user.id == article.author_id:
        response = {
            "like_count": get_count_post_likes(pk),
            "dislike_count": get_count_post_dislikes(pk),
            "author_liked": False,
            "author_disliked": False,
            "rating_count": article.rating,
        }
        return JsonResponse(response)
    else:
        to_score_post(user, pk, "dislike")
        article = get_article(pk)

        response = {
            "like_count": get_count_post_likes(pk),
            "dislike_count": get_count_post_dislikes(pk),
            "author_liked": check_post_liked(user, pk),
            "author_disliked": check_post_disliked(user, pk),
            "rating_count": article.rating,
        }
        return JsonResponse(response)

@csrf_exempt
def like_dislike_comment_ajax(request, pk=None, template="mainapp/comment.html"):
    user = get_current_user(request)
    if request.is_ajax() and request.method == "POST":
        parent_id = int(request.POST.get("id_dt"))
        type = request.POST.get("type")
        #pk = request.POST.get("pk")
        if type == "dl":
            to_score_comment(user, parent_id, "dislike")
        elif type == "lk":
            to_score_comment(user, parent_id, "like")
        elif type.find("repcom") > -1:
            print(type.find("repcom"))    
    else:
        pass
    article = get_article(pk)
    comments = article.comment.filter(main_parent__isnull=True)
    content = {
        "post": get_article(pk),
        "categories": get_category_list,
        "all_comments": comments,
        "media_url": settings.MEDIA_URL,
        "like_comment": read_comment_like(request, pk),
        "dislike_comment": read_comment_dislike(request, pk),
        "alert": count_alerts(request),
        "ban": ban_is_active(user.id),
        "ban_info": get_ban_obj(user.id),
    }

    return render(request, "mainapp/comment.html", content)

def like_comment(request, pk=None):
    user = get_current_user(request)
    comment = get_comment(pk)
    article_id = comment.article_id
    if user.id == comment.author_comment_id:
        return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": article_id}))
    else:
        to_score_comment(user, comment.id, "like")
        return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": article_id}))


def dislike_comment(request, pk=None):
    user = get_current_user(request)
    comment = get_comment(pk)
    article_id = comment.article_id
    if user.id == comment.author_comment_id:
        return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": article_id}))
    else:
        to_score_comment(user, comment.id, "dislike")
        return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": article_id}))


def comments_count(request, pk=None):
    time.sleep(1)
    article = get_article(pk)
    response = {"comments_count": article.comments_count}
    print(article.comments_count)
    return JsonResponse(response)


def main(request, sorted_by="-published_at"):
    timezone.activate(pytz.timezone(str(get_localzone())))
    title = "главная"
    print(str(get_localzone()))
    post_list = get_articles(sorted_by=sorted_by)
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 5)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    content = {
        "title": title,
        "posts": posts,
        "categories": get_category_list,
        "sorting_criteria": get_list_of_sorting_criteria_for_articles(),
        "user": get_current_user(request),
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }

    if request.is_ajax():
        posts = render_to_string(
            "mainapp/includes/inc__articles_list.html", content)
        return JsonResponse({"posts": posts})
    return render(request, "mainapp/index.html", content)


def hubs(request, slug, sorted_by="-published_at"):
    timezone.activate(pytz.timezone(str(get_localzone())))
    category = get_object_or_404(Category, slug=slug)
    title = category.name
    content = {
        "title": title,
        "category": category,
        "posts": get_articles(category, sorted_by=sorted_by),
        "categories": get_category_list,
        "sorting_criteria": get_list_of_sorting_criteria_for_articles(),
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
    }
    if request.is_ajax():
        posts = render_to_string("mainapp/includes/inc__articles_list.html", content)
        return JsonResponse({"posts": posts})
    return render(request, "mainapp/index.html", content)


@csrf_exempt
def post_complaint(request, pk=None):
    """Заполняем таблицу данными по статье, юзеру и жалобе к статье"""
    article = get_article(pk)
    user = get_current_user(request)
    message = request.POST["complain_text"]
    if len(message.strip()) > 1:
        try:
            Complaint.objects.create(
                article=article,
                submitted_user=user,
                complaint_text=message,
            )
        except Exception:
            pass

    return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": pk}))


@csrf_exempt
def comment_complaint(request, pk=None):
    """Заполняем таблицу данными по комментарию, юзеру и жалобе к комментарию"""
    comment = get_comment_for_complaint(pk)  # получили объект комментария
    # из него получили id статьи для reverse (пока нет ajax)
    article_id = comment.article_id
    user = get_current_user(request)
    message = request.POST["comment_complain_text"]
    if len(message.strip()) > 1:
        try:
            Complaint.objects.create(
                comment=comment,
                submitted_user=user,
                complaint_text=message,
            )
        except Exception:
            pass

    return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": article_id}))


def search(request):
    search_request_original = request.GET.get("search_request")
    search_filter = request.GET.get("filter")
    search_request = search_request_original
    title = "Поиск"
    if search_request_original:
        title = title + f" - {search_request_original}"
        search_request = search_request_original.lower()

    content = {
        "title": title,
        "categories": get_category_list,
        "user": get_current_user(request),
        "media_url": settings.MEDIA_URL,
        "alert": count_alerts(request),
        "search_request": search_request_original,
    }

    if request.is_ajax():
        search_output = perform_search(search_request, search_filter, content, is_ajax=True)
        return JsonResponse({"search_output": search_output})
    else:
        if search_request and len(search_request) > 0:
            if search_filter == 'posts':
                content["posts"] = perform_search(search_request, "posts", content)
            elif search_filter == 'comments':
                content["comments"] = perform_search(search_request, "comments", content)
            elif search_filter == 'users':
                content["users"] = perform_search(search_request, "users", content)
        content["filter"] = search_filter
    return render(request, "mainapp/search_result.html", content)


def get_audio_name(audio_name):
    audio = open(f"media/article_audio/{audio_name}", "rb")
    response = FileResponse(audio)
    return response


def get_audio_block(request):
    if request.is_ajax():
        article_id = request.GET.get("article_id")
        article = get_article(article_id)
        content = {
            "post": article,
            "article": article,
            "audio_url": os.path.join("\\media\\article_audio", article.audio_name),
        }
        audio_block = render_to_string("lkapp/includes/inc__lkapp_audio_block.html", content)
        if "article-" in article.audio_name:
            status = "done"
        else:
            status = article.audio_name
        response = {"audio_block": audio_block, "status": status}
        return JsonResponse(response)


def regenerate_audio(request):
    if request.is_ajax():
        article_id = int(request.GET.get("article_id"))
        article = get_article(article_id)
        generate_article_audio(article)
        return HttpResponse('')
    content = {
        "categories": get_category_list,
        "user": get_current_user(request),
        "alert": count_alerts(request),
    }
    return render(request, "lkapp/errors/access_error.html", content)

# Старый контроллер комментариев
@csrf_exempt
def comment_ajax(request, pk=None, template="mainapp/comment.html"):
    # тк комментарии обновляются после добавления новых - также используем блок работы со временем
    timezone.activate(pytz.timezone(str(get_localzone())))
    article = get_article(pk)

    comments = article.comment.filter(main_parent__isnull=True)
    if request.method == "POST":
        comment_form = Add_Comment_Form(request.POST)
        if comment_form.is_valid():
            try:
                main_parent_id = int(request.POST.get("main_parent"))
            except:
                main_parent_id = None
            if main_parent_id:
                main_parent_obj = Comments.objects.get(id=main_parent_id)
                if main_parent_obj:
                    replay_comment = comment_form.save(commit=False)
                    replay_comment.main_parent = main_parent_obj
            try:
                parent_id = int(request.POST.get("parent"))
            except:
                parent_id = None
            if parent_id:
                main_parent_id = int(request.POST.get("main_parent"))
                main_parent_obj = Comments.objects.get(id=main_parent_id)
                parent_obj = Comments.objects.get(id=parent_id)
                if parent_obj:
                    replay_comment = comment_form.save(commit=False)
                    replay_comment.main_parent = main_parent_obj
                    replay_comment.parent = parent_obj

            new_comment = comment_form.save(commit=False)
            new_comment.author_comment = get_current_user(request)
            new_comment.article = article
            article.comments_count += 1
            new_comment.comment_text = comment_form.cleaned_data["comment_text"]
            new_comment.save()
            article.save()
            SaveAlert(action_user=request.user, post=article, comment=new_comment, event_type="comment")
        title = "Чтение статьи"
        content = {
            "title": title,
            "post": get_article(pk),
            "categories": get_category_list,
            "all_comments": comments,
            "comment_form": comment_form,
            "media_url": settings.MEDIA_URL,
            "like_comment": read_comment_like(request, pk),
            "dislike_comment": read_comment_dislike(request, pk),
            "alert": count_alerts(request),
            "ban": ban_is_active(request.user.id),
            "ban_info": get_ban_obj(request.user.id),
        }

        return render(request, template, content)

    else:
        return HttpResponseRedirect(reverse("main:read_post", kwargs={"pk": pk}))

