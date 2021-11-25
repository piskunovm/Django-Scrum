from django.core.exceptions import ObjectDoesNotExist
from ...models import UserSettings
from authapp.models import User
from lkapp.models import Alert
from mainapp.models import Comments, Article, Complaint, UserBan


def get_alerts(request, url_ajax = None):
    url = request.get_full_path().strip("/").split("/")[-1]
    if url_ajax != None: url = url_ajax
    try:
        if url == "my_alerts" or url == "my_alerts_ajax":
            qs = Alert.objects.filter(
                alert_user_id=request.user.id).order_by("-created_at")
        elif url == "comment_alerts" or url == "comment_alerts_ajax":
            qs = Alert.objects.filter(alert_user_id=request.user.id,
                                      event_type="comment").order_by("-created_at")
        elif url == "grade_alerts" or url == "grade_alerts_ajax":
            qs = Alert.objects.filter(alert_user_id=request.user.id,
                                      event_type__in=["post_like",
                                                      "post_dislike",
                                                      "author_like",
                                                      "author_dislike"]).order_by("-created_at")
        elif url == "moder_alerts" or url == "moder_alerts_ajax":
            qs = Alert.objects.filter(alert_user_id=request.user.id,
                                      event_type__in=["approve_status",
                                                      "reject_status",
                                                      "approve_complaint_post_sub",
                                                      "approve_complaint_post_bu",
                                                      "reject_complaint_post",
                                                      "reject_complaint_comment",
                                                      "approve_complaint_comment_sub",
                                                      "approve_complaint_comment_bu",
                                                      "user_ban"]).order_by("-created_at")
        elif url == "subscribe_alerts" or url == "subscribe_alerts_ajax":
            qs = Alert.objects.filter(alert_user_id=request.user.id,
                                      event_type__in=["new_post_sub",
                                                      "author_unsubscribe",
                                                      "author_subscribe"]).order_by("-created_at")
        return qs
    except ObjectDoesNotExist:
        return False


def get_comment(id):
    try:
        comment = Comments.objects.get(id=id)
        return comment
    except ObjectDoesNotExist:
        return False


def get_article(id):
    try:
        article = Article.objects.get(id=id)
        return article
    except ObjectDoesNotExist:
        return False


def get_username(id):
    try:
        username = User.objects.get(id=id).username
        return username
    except ObjectDoesNotExist:
        return False


def get_email(id):
    try:
        email = User.objects.get(id=id).email
        return email
    except ObjectDoesNotExist:
        return False


def get_comlaint(id):
    try:
        comlaint = Complaint.objects.get(id=id)
        return comlaint
    except ObjectDoesNotExist:
        return False


def get_ban(id):
    try:
        ban = UserBan.objects.get(id=id)
        return ban
    except ObjectDoesNotExist:
        return False


def set_mail_settings(id):
    try:
        settings = UserSettings.objects.get(id=id)
        if settings.email_alerts_is_on:
            settings.email_alerts_is_on = False
        else:
            settings.email_alerts_is_on = True
        settings.save()
        return settings.email_alerts_is_on
    except ObjectDoesNotExist:
        return False


def get_mail_settings(id):
    try:
        settings = UserSettings.objects.get(id=id)
        return settings.email_alerts_is_on
    except ObjectDoesNotExist:
        return False