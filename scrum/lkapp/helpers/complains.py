from datetime import datetime, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse

from lkapp.helpers.alerts.alert import SaveAlert
from lkapp.helpers.posts import PostFlow
from lkapp.helpers.rating_author import author_rate_low_before_complain
from mainapp.helpers.article.article import get_article
from mainapp.models import Complaint, Comments


class ComplainFlow:
    def __init__(self, action):
        self.action = action
        self.next_status = self.flow()

    def flow(self):
        try:
            if self.action == "moderated":
                return "processed"
            elif self.action == "approve":
                return "processed"
        except ValueError:
            print("Error in action. Check request")

    def __str__(self):
        return self.next_status


def set_complain_status(request, pk, action):
    complain = Complaint.objects.get(pk=pk)
    complain.moderator_id = request.user.id
    comment_moderator = request.GET["comment_moderator"]
    complain.moderator_comment = comment_moderator
    complain.updated_at = datetime.now(timezone.utc)

    if action == "moderated":
        complain.status = ComplainFlow(action)
        complain.updated_at = datetime.now(timezone.utc)
        complain.moderator_comment = comment_moderator
        if complain.article_id:
            SaveAlert(action_user=request.user, complaint=complain, event_type="reject_complaint_post")
        if complain.comment_id:
            SaveAlert(action_user=request.user, complaint=complain, event_type="reject_complaint_comment")

    elif action == "approve":
        # блок работы с таблицей Article
        complain.status = ComplainFlow(action)
        if complain.article_id:
            article_id = complain.article.id
            article = get_article(article_id)
            article.status = PostFlow("correcting")
            article.moderator_id = request.user.id
            article.comment_moderator = comment_moderator
            article.save()
            # Функция понижает рейтинг автора
            author_rate_low_before_complain(article.author)
            SaveAlert(
                action_user=request.user, post=article, complaint=complain, event_type="approve_complaint_post_sub"
            )
            SaveAlert(
                action_user=request.user, post=article, complaint=complain, event_type="approve_complaint_post_bu"
            )

        # блок работы с таблицей Comments
        if complain.comment_id:
            comment_id = complain.comment.id
            comment = Comments.objects.get(pk=comment_id)
            article_id = comment.article.id
            article = get_article(article_id)
            SaveAlert(
                action_user=request.user, comment=comment, complaint=complain, event_type="approve_complaint_comment_sub"
            )
            SaveAlert(
                action_user=request.user, comment=comment, complaint=complain, event_type="approve_complaint_comment_bu"
            )
            comment.delete()

    complain.save()
    return HttpResponseRedirect(reverse(f"my_lk:my_complains"))


def get_complains_on_moderation(request):
    try:
        if request.user.user_role == "moderator" or request.user.user_role == "administrator":
            complains = Complaint.objects.filter(status="active").order_by("-created_at")
            return complains
        else:
            return False
    except ObjectDoesNotExist:
        return False


def get_complains_posts_on_moderation(request):
    try:
        if request.user.user_role == "moderator" or request.user.user_role == "administrator":
            all_complains = Complaint.objects.filter(status="active").order_by("-created_at")
            post_complains = []
            for complain in all_complains:
                if complain.comment is None:
                    post_complains.append(complain)
            return post_complains
        else:
            return False
    except ObjectDoesNotExist:
        return False


def get_complains_comments_on_moderation(request):
    try:
        if request.user.user_role == "moderator" or request.user.user_role == "administrator":
            all_complains = Complaint.objects.filter(status="active").order_by("-created_at")
            comment_complains = []
            for complain in all_complains:
                if complain.article is None:
                    comment_complains.append(complain)
            return comment_complains
        else:
            return False
    except ObjectDoesNotExist:
        return False
