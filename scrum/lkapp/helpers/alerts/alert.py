from . import get_comment, get_username, get_article, get_comlaint, get_ban
from scrum.settings import FOREVER
from ...models import Alert



def count_alerts(request):
    """считает кол-во активных уведомлений по юзеру"""
    try:
        total_alerts = Alert.objects.filter(alert_user_id=request.user.id, not_read=True).count()
        return total_alerts
    except TypeError:
        pass
    return 0


class SaveAlert:
    """Класс формирует данные по алертам"""

    def __init__(self, event_type=None, post=None, alert_user=None, followers=None, like=None, complaint=None, comment=None,
                 subscription=None, action_user=None, ban=None):
        self.event_type = event_type
        self.post = post
        self.like = like
        self.comment = comment
        self.subscription = subscription
        self.complaint = complaint
        self.action_user = action_user
        self.alert_user = alert_user
        self.followers = followers
        self.ban = ban

        self.entry = self.create_entry()

    def create_entry(self):
        try:
            if self.event_type == "comment":
                Alert.objects.create(alert_user_id=self.post.author_id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.comment.id,
                                     event_type=self.event_type)
            elif self.event_type == "post_like" or self.event_type == "post_dislike":
                Alert.objects.create(alert_user_id=self.post.author_id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.like.article_id,
                                     event_type=self.event_type)
            elif self.event_type == "approve_status" or self.event_type == "reject_status":
                Alert.objects.create(alert_user_id=self.post.author_id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.post.id,
                                     event_type=self.event_type)
            elif self.event_type == "author_like":
                Alert.objects.create(alert_user_id=self.like.score_user_id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.action_user.id,
                                     event_type=self.event_type)
            elif self.event_type == "author_dislike":
                Alert.objects.create(alert_user_id=self.like.score_user_id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.action_user.id,
                                     event_type=self.event_type)
            elif self.event_type == "approve_complaint_post_sub":
                Alert.objects.create(alert_user_id=self.complaint.submitted_user_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.article_id,
                                     event_type=self.event_type)
            elif self.event_type == "reject_complaint_post":
                Alert.objects.create(alert_user_id=self.complaint.submitted_user_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.id,
                                     event_type=self.event_type)
            elif self.event_type == "approve_complaint_post_bu":
                Alert.objects.create(alert_user_id=self.post.author_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.article_id,
                                     event_type=self.event_type)
            elif self.event_type == "approve_complaint_comment_sub":
                Alert.objects.create(alert_user_id=self.complaint.submitted_user_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.comment_id,
                                     event_type=self.event_type)
            elif self.event_type == "reject_complaint_comment":
                Alert.objects.create(alert_user_id=self.complaint.submitted_user_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.id,
                                     event_type=self.event_type)
            elif self.event_type == "approve_complaint_comment_bu":
                Alert.objects.create(alert_user_id=self.comment.author_comment_id,
                                     action_user_id=self.complaint.moderator_id,
                                     parent_obj=self.complaint.id,
                                     event_type=self.event_type)
            elif self.event_type == "author_subscribe" or self.event_type == "author_unsubscribe":
                Alert.objects.create(alert_user_id=self.alert_user.id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.action_user.id,
                                     event_type=self.event_type)
            elif self.event_type == "new_post_sub":
                for follower in self.followers:
                    Alert.objects.create(alert_user_id=follower.id,
                                         action_user_id=self.post.author_id,
                                         parent_obj=self.post.id,
                                         event_type=self.event_type)
            elif self.event_type == "user_ban":
                Alert.objects.create(alert_user_id=self.alert_user.id,
                                     action_user_id=self.action_user.id,
                                     parent_obj=self.ban.id,
                                     event_type=self.event_type)
        except AttributeError:
            return "Error: wrong attribute"


class AlertFrontHandler(object):
    """Класс возвращает данные по алертам"""

    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        for obj in self.queryset:
            if obj.event_type == "comment":
                comment = get_comment(obj.parent_obj)
                username = get_username(obj.action_user_id)
                setattr(obj, "comment", comment.comment_text)
                setattr(obj, "icon", "vendor/img_for_alerts/chat-left-text-fill.svg")
                setattr(obj, "system_text",
                        f"У вас новый комментарий от")
                setattr(obj, "parent_url", f"/post/{comment.article_id}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "post_like":
                post = get_article(obj.parent_obj)
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-smile.svg")
                setattr(obj, "system_text",
                        f'нравится ваша статья "{post.title}"')
                setattr(obj, "parent_url", f"/post/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "post_dislike":
                post = get_article(obj.parent_obj)
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-frown-fill.svg")
                setattr(obj, "system_text",
                        f'не нравится ваша статья "{post.title}"')
                setattr(obj, "parent_url", f"/post/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "approve_status":
                post = get_article(obj.parent_obj)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text",
                        f'Ваша статья "{post.title}" успешно прошла модерацию!')
                setattr(obj, "parent_url", f"/my_lk/myposts/")
                yield obj
            elif obj.event_type == "reject_status":
                post = get_article(obj.parent_obj)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(
                    obj, "system_text", f'К сожалению ваша статья "{post.title}" не прошла модерацию!')
                setattr(obj, "parent_url", f"/my_lk/myposts/")
                yield obj
            elif obj.event_type == "approve_complaint_comment_sub":
                username = get_username(obj.action_user_id)
                comment = get_comment(obj.parent_obj)
                post = get_comment(comment.article_id)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'Cпасибо за бдительность, комментарий удален! {comment.comment_text}')
                setattr(obj, "parent_url", f"/post/{post.id}/")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "approve_complaint_comment_bu":
                username = get_username(obj.action_user_id)
                complaint = get_comlaint(obj.parent_obj)
                comment = get_comment(complaint.comment_id)
                post = get_article(comment.article_id)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'Ваш комментарий удален модератором! {comment.comment_text}')
                setattr(obj, "comment", f' Причина: {complaint.moderator_comment}.')
                setattr(obj, "parent_url", f"/post/{post.id}/")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "reject_complaint_comment":
                username = get_username(obj.action_user_id)
                complaint = get_comlaint(obj.parent_obj)
                comment = get_comment(complaint.comment_id)
                post = get_article(comment.article_id)
                setattr(obj, "comment", f' Причина: {complaint.moderator_comment}.')
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text",
                        f'Ваша жалоба на комментарий отклонена модератором! {comment.comment_text}')
                setattr(obj, "parent_url", f"/post/{post.id}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "author_like":
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-smile.svg")
                setattr(obj, "system_text", f'Вы нравитесь')
                setattr(obj, "parent_url", f"/user/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "author_dislike":
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-frown-fill.svg")
                setattr(obj, "system_text", f'Вы не нравитесь')
                setattr(obj, "parent_url", f"/user/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "approve_complaint_post_sub":
                username = get_username(obj.action_user_id)
                post = get_article(obj.parent_obj)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'Cпасибо за бдительность! Ваша жалоба на статью - "{post.title}" - одобрена!')
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "approve_complaint_post_bu":
                username = get_username(obj.action_user_id)
                post = get_article(obj.parent_obj)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'Ваша статья - "{post.title}" требует исправлений!')
                setattr(obj, "parent_url", f"/my_lk/myposts/")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "reject_complaint_post":
                username = get_username(obj.action_user_id)
                complaint = get_comlaint(obj.parent_obj)
                post = get_article(complaint.article_id)
                setattr(obj, "comment", complaint.moderator_comment)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'Ваша жалоба на статью - "{post.title}" отклонена модератором')
                setattr(obj, "parent_url", f"/post/{complaint.article_id}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "author_subscribe":
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-smile.svg")
                setattr(obj, "system_text", f'На Вас подписался')
                setattr(obj, "parent_url", f"/user/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "author_unsubscribe":
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/emoji-frown.svg")
                setattr(obj, "system_text", f'От Вас отписался')
                setattr(obj, "parent_url", f"/user/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "new_post_sub":
                post = get_article(obj.parent_obj)
                username = get_username(obj.action_user_id)
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                setattr(obj, "system_text", f'опубликовал новую статью "{post.title}"!')
                setattr(obj, "parent_url", f"/post/{obj.parent_obj}")
                setattr(obj, "username", username)
                yield obj
            elif obj.event_type == "user_ban":
                ban = get_ban(obj.parent_obj)
                username = get_username(obj.action_user_id)
                delta = ban.ban_end_time - ban.created_at
                result = delta.days * 1440 + 639
                setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
                if result == FOREVER:
                    setattr(obj, "system_text", f'заблокировал ваш аккаунт. Время блокировки - "Бессрочный"!')
                else:
                    setattr(obj, "system_text", f'заблокировал ваш аккаунт. Время блокировки - "{ban.ban_end_time}"!')
                setattr(obj, "parent_url", f"/user/{obj.alert_user_id}")
                setattr(obj, "reason", f"Причина: '{ban.reason}'")
                setattr(obj, "username", username)
                yield obj
