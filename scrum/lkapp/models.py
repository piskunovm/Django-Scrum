from django.db import models

from authapp.models import User
from mainapp.models import Article


class Alert(models.Model):
    """Модель содержащая данные по уведомлениям"""

    alert_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alert_user")
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="action_user")

    class EventType(models.TextChoices):
        comment = "comment"
        answer = "answer"
        post_like = "post_like"
        post_dislike = "post_dislike"
        new_post_sub = "new_post_sub"
        comment_like = "comment_like"
        comment_dislike = "comment_dislike"
        answer_like = "answer_like"
        answer_dislike = "answer_dislike"
        author_like = "author_like"
        author_dislike = "author_dislike"
        approve_status = "approve_status"
        reject_status = "reject_status"
        another_status = "another_status"
        author_subscribe = "author_subscribe"
        author_unsubscribe = "author_unsubscribe"
        approve_complaint_post_sub = "approve_complaint_post_sub"
        approve_complaint_post_bu = "approve_complaint_post_bu"
        reject_complaint_post = "reject_complaint_post"
        approve_complaint_comment_sub = "approve_complaint_comment_sub"
        approve_complaint_comment_bu = "approve_complaint_comment_bu"
        reject_complaint_comment = "complaint_comment"
        user_ban = "user_ban"

    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
        verbose_name="Тип события",
    )

    parent_obj = models.IntegerField(verbose_name="id объекта", null=True)
    not_read = models.BooleanField(verbose_name="Не прочитано", blank=False, null=False, default=True)
    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)

    class Meta:
        verbose_name = "Оповещения"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.event_type, self.alert_user


class UserSettings(models.Model):
    """Модель содержащая настройки пользователя"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_settings")
    email_alerts_is_on = models.BooleanField(verbose_name="уведомления на почту", blank=False, null=False, default=True)
    lk_alerts_is_on = models.BooleanField(verbose_name="уведомления в лк", blank=False, null=False, default=True)

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = verbose_name


class UserSettingsLog(models.Model):
    """Модель содержащая лог изменений настроек пользователя"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_log")

    switched_setting = models.TextField(verbose_name="описание", max_length=64, blank=False, null=False)
    created_at = models.DateTimeField(verbose_name="изменено", editable=False, auto_now_add=True)

    class Meta:
        verbose_name = "Лог изменений"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user} change {self.switched_setting}'
