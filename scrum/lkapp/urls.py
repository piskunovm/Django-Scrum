from django.urls import path

import lkapp.views as lkapp

app_name = "lkapp"

urlpatterns = [
    # Профиль
    path("profile/<int:pk>/", lkapp.my_profile, name="my_profile"),
    path("profile/<int:pk>/update", lkapp.profile_update, name="profile_update"),
    path("profile/<int:pk>/delete", lkapp.delete_user, name="delete_user"),
    path("profile/<int:pk>/set_email_settings", lkapp.set_mail_settting_switcher, name="switch_email_settings"),
    # Ajax-mail_checked
    path("profile/<int:pk>/switch_email_settings_ajax", lkapp.set_mail_settting_switcher,
         name="switch_email_settings_ajax"),
    # Статьи/Черновики
    path("post/create/", lkapp.post_creation, name="post_creation"),
    path("myposts/", lkapp.my_posts, name="my_posts"),
    path("myposts/published", lkapp.my_posts_ajax, name="published"),
    path("myposts/moderation", lkapp.my_posts_ajax, name="moderation"),
    path("myposts/correction", lkapp.my_posts_ajax, name="correction"),
    path("myposts/archive", lkapp.my_posts_ajax, name="archive"),
    path("myposts/myposts", lkapp.my_posts_ajax, name="myposts_ajax"),
    path("draft/", lkapp.my_drafts, name="drafts"),
    path("draft/<int:pk>/", lkapp.preview_draft, name="read_draft"),
    path("draft/<int:pk>/moderation", lkapp.publicating_post,
         name="go_on_moderation_post"),
    path("draft/<int:pk>/delete", lkapp.delete_drafts, name="delete_drafts"),
    path("myposts/<int:pk>/", lkapp.preview_post, name="preview_post"),
    path("myposts/<int:pk>/publicate",
         lkapp.publicating_post, name="publicate_post"),
    path("myposts/<int:pk>/deactivate",
         lkapp.archivating_post, name="deactivate_post"),
    path("posts_moderation/", lkapp.posts_on_moderation,
         name="posts_for_moderation"),
    path("post_moderation/<int:pk>/",
         lkapp.post_moderation, name="post_moderation"),
    path(
        "post_moderation/<int:pk>/correction/",
        lkapp.set_article_status_correction,
        name="set_article_status_correction",
    ),
    path(
        "post_moderation/<int:pk>/published/", lkapp.set_article_status_published, name="set_article_status_published"
    ),
    path("myposts/<int:pk>/edit", lkapp.edit_post, name="edit_post"),
    path("draft/<int:pk>/edit", lkapp.edit_draft, name="edit_draft"),

    # Уведомления
    path("my_alerts/", lkapp.my_alerts, name="my_alerts"),
    path("my_alerts/comment_alerts", lkapp.my_alerts, name="comment_alerts"),
    path("my_alerts/grade_alerts", lkapp.my_alerts, name="grade_alerts"),
    path("my_alerts/moder_alerts", lkapp.my_alerts, name="moder_alerts"),
    path("my_alerts/subscribe_alerts", lkapp.my_alerts, name="subscribe_alerts"),
    # Кнопки уведомлений

    # ajax меню блока Alerts++
    path("my_alerts/my_alerts_ajax", lkapp.my_alerts_ajax, name="my_alerts_ajax"),
    path("my_alerts/comment_alerts_ajax",
         lkapp.my_alerts_ajax, name="comment_alerts_ajax"),
    path("my_alerts/grade_alerts_ajax",
         lkapp.my_alerts_ajax, name="grade_alerts_ajax"),
    path("my_alerts/moder_alerts_ajax",
         lkapp.my_alerts_ajax, name="moder_alerts_ajax"),
    path("my_alerts/subscribe_alerts_ajax",
         lkapp.my_alerts_ajax, name="subscribe_alerts_ajax"),
    # ajax меню блока Alerts--

    path("delete_all_alerts/", lkapp.delete_all_alerts, name="delete_all_alerts"),
    path("delete_read_alerts/", lkapp.delete_read_alerts,
         name="delete_read_alerts"),
    path("delete_alert/<int:pk>/", lkapp.delete_alert, name="delete_alert"),
    path("mark_as_read/<int:pk>/", lkapp.mark_as_read, name="mark_as_read"),

    # Жалобы
    path("complains/", lkapp.my_complains, name="my_complains"),
    path("complains/complains", lkapp.my_complains_ajax, name="my_complains_ajax"),
    path("complains/complain_posts", lkapp.my_complains_post_ajax, name="my_complains_post_ajax"),
    path("complains/complain_comments", lkapp.my_complains_comments_ajax, name="my_complains_comments_ajax"),
    path("complains/moderation/<int:pk>/", lkapp.complain_moderation, name="complain_moderation"),
    path("complains/moderation/<int:pk>/denied/", lkapp.set_complain_status_denied,
         name="set_complain_status_denied"),
    path("complains/moderation/<int:pk>/approve/", lkapp.set_complain_status_approve,
         name="set_complain_status_approve"),
    # Подписки
    path("mysubscribes/", lkapp.my_subscribes, name="my_subscribes"),
]
