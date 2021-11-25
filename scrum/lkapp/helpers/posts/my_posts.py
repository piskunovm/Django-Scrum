from datetime import datetime, timezone

from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.http import HttpResponseRedirect
from django.urls import reverse

from lkapp.helpers.alerts.alert import SaveAlert
from lkapp.helpers.follow import get_followers
from lkapp.helpers.posts import PostFlow
from lkapp.helpers.rating_author import (
    get_rate_author,
    RATE_FOR_PUBLICATED_WITHOUT_MODERATING,
    author_rate_up_before_publicated,
)
from mainapp.helpers.article.article import get_article
from mainapp.models import Article


def get_articles(request, sorted_by="-created_at"):
    url = request.get_full_path().strip("/").split("/")[-1]
    try:
        if url == "myposts":
            excludes = ["draft", "inactive"]
            articles = Article.objects.filter(author=request.user.id).exclude(status__in=excludes).order_by(sorted_by)
        else:
            articles = Article.objects.filter(author=request.user.id, status=url).order_by(sorted_by)
        return articles
    except ObjectDoesNotExist:
        return False


def get_articles_on_moderation(request, sorted_by="-created_at"):
    try:
        if request.user.user_role == "moderator" or request.user.user_role == "administrator":
            articles = Article.objects.filter(status="moderation").order_by(sorted_by)
            return articles
        else:
            return False
    except ObjectDoesNotExist:
        return False


def publicate_post(request, pk, post_status):
    try:
        post = Article.objects.get(author_id=request.user.id, id=pk)
        if post_status == "draft":
            if get_rate_author(request.user.id) >= RATE_FOR_PUBLICATED_WITHOUT_MODERATING:
                post.status = PostFlow("moderated", post)
                post.published_at = datetime.now(timezone.utc)
                post.save()
                followers = get_followers(post.author_id)
                if followers:
                    SaveAlert(action_user=post.author_id, post=post, followers=followers, event_type="new_post_sub")
            else:
                post.status = PostFlow("publicate")
                post.save()
        if post_status == "published":
            if get_rate_author(request.user.id) >= RATE_FOR_PUBLICATED_WITHOUT_MODERATING:
                pass
            else:
                post.status = PostFlow("publicate")
                post.save()
        if post_status == "correction":
            post.status = PostFlow("publicate")
            post.save()
        return True
    except ObjectDoesNotExist:
        return False
    except FieldError:
        return False


def archivate_post(request, pk):
    try:
        post = Article.objects.get(author_id=request.user.id, id=pk)
        post.status = PostFlow("archivate")
        post.save()
        return True
    except ObjectDoesNotExist:
        return False
    except FieldError:
        return False


def delete_draft(request, pk):
    try:
        post = Article.objects.get(author_id=request.user.id, id=pk)
        post.status = PostFlow("delete")
        post.save()
        return True
    except ObjectDoesNotExist:
        return False
    except FieldError:
        return False


def set_article_status(request, pk, action):
    article = get_article(pk)
    article.status = PostFlow(action, article)
    try:  # блок для работы с id модератора
        id_moderator = request.user.id  # получаем ID модератора
        article.moderator_id = id_moderator
    except Exception:
        pass
    try:
        comment_moderator = request.GET["comment_moderator"]
        article.comment_moderator = comment_moderator
    except Exception:
        pass

    if action == "moderated":
        article.published_at = datetime.now(timezone.utc)
    article.save()
    author_rate_up_before_publicated(article.author_id)
    if action == "moderated":
        SaveAlert(action_user=request.user, post=article, event_type="approve_status")
        followers = get_followers(article.author_id)
        if followers:
            SaveAlert(action_user=article.author_id, post=article, followers=followers, event_type="new_post_sub")
    else:
        SaveAlert(action_user=request.user, post=article, event_type="reject_status")
    return HttpResponseRedirect(reverse(f"my_lk:posts_for_moderation"))
