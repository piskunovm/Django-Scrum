from . import get_comment, get_username, get_article, get_comlaint, get_ban


def mail_content(obj):
    if obj.event_type == "comment":
        comment = get_comment(obj.parent_obj)
        username = get_username(obj.action_user_id)
        setattr(obj, "comment", comment.comment_text)
        setattr(obj, "system_text", f" написал новый комментарий")
        setattr(obj, "parent_url", f"http://inengb.ru/post/{comment.article_id}")
        setattr(obj, "username", username)
    elif obj.event_type == "post_like":
        post = get_article(obj.parent_obj)
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' нравится ваша статья "{post.title}"')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "post_dislike":
        post = get_article(obj.parent_obj)
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' не нравится ваша статья "{post.title}"')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "approve_status":
        post = get_article(obj.parent_obj)
        setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
        setattr(obj, "system_text", f'Ваша статья "{post.title}" успешно прошла модерацию!')
        setattr(obj, "parent_url", f"http://inengb.ru/my_lk/myposts/")
    elif obj.event_type == "reject_status":
        post = get_article(obj.parent_obj)
        setattr(obj, "system_text", f'К сожалению ваша статья "{post.title}" не прошла модерацию!')
        setattr(obj, "parent_url", f"http://inengb.ru/my_lk/myposts/")
    elif obj.event_type == "author_like":
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' выразил симпатию к Вам')
        setattr(obj, "parent_url", f"http://inengb.ru/user/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "author_dislike":
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' выразил антисимпатию к Вам')
        setattr(obj, "parent_url", f"http://inengb.ru/user/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "approve_complaint_post_sub":
        username = get_username(obj.action_user_id)
        post = get_article(obj.parent_obj)
        setattr(obj, "system_text", f'Cпасибо за бдительность! Статья - "{post.title}" заблокирована!')
        setattr(obj, "username", username)
    elif obj.event_type == "approve_complaint_post_bu":
        username = get_username(obj.action_user_id)
        post = get_article(obj.parent_obj)
        setattr(obj, "system_text", f'Ваша статья - "{post.title}" заблокирована!')
        setattr(obj, "parent_url", f"http://nengb.ru/my_lk/myposts/")
        setattr(obj, "username", username)
    elif obj.event_type == "reject_complaint_post":
        username = get_username(obj.action_user_id)
        complaint = get_comlaint(obj.parent_obj)
        post = get_article(complaint.article_id)
        setattr(obj, "comment", complaint.moderator_comment)
        setattr(obj, "system_text", f'Ваша жалоба на статью - "{post.title}" отклонена модератором')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{complaint.article_id}")
        setattr(obj, "username", username)
    elif obj.event_type == "approve_complaint_comment_sub":
        username = get_username(obj.action_user_id)
        comment = get_comment(obj.parent_obj)
        post = get_comment(comment.article_id)
        setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
        setattr(obj, "system_text", f'Cпасибо за бдительность! Комментарий - "{comment.comment_text}" удален!')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{post.id}/")
        setattr(obj, "username", username)
    elif obj.event_type == "approve_complaint_comment_bu":
        username = get_username(obj.action_user_id)
        comment = get_comment(obj.parent_obj)
        post = get_article(comment.article_id)
        setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
        setattr(obj, "system_text", f'Ваш комментарий - "{comment.comment_text}" удален модератором!')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{post.id}/")
        setattr(obj, "username", username)
    elif obj.event_type == "reject_complaint_comment":
        username = get_username(obj.action_user_id)
        complaint = get_comlaint(obj.parent_obj)
        comment = get_comment(obj.parent_obj)
        setattr(obj, "comment", complaint.moderator_comment)
        setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
        setattr(obj, "system_text",
                f'Ваша жалоба на комментарий - "{comment.comment_text}" отклонена модератором')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{complaint.article_id}")
        setattr(obj, "username", username)
    elif obj.event_type == "author_subscribe":
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' подписался на Вас')
        setattr(obj, "parent_url", f"http://inengb.ru/user/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "author_unsubscribe":
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f' отписался от Вас')
        setattr(obj, "parent_url", f"http://inengb.ru/user/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "new_post_sub":
        post = get_article(obj.parent_obj)
        username = get_username(obj.action_user_id)
        setattr(obj, "system_text", f'Новый пост "{post.title}" от')
        setattr(obj, "parent_url", f"http://inengb.ru/post/{obj.parent_obj}")
        setattr(obj, "username", username)
    elif obj.event_type == "user_ban":
        ban = get_ban(obj.parent_obj)
        username = get_username(obj.action_user_id)
        setattr(obj, "icon", "vendor/img_for_alerts/file-post.svg")
        setattr(obj, "system_text", f'заблокировал ваш аккаунт. Время блокировки - "{ban.ban_end_time}"!')
        setattr(obj, "parent_url", f"http://inengb.ru/user/{obj.alert_user_id}")
        setattr(obj, "reason", f"Причина: '{ban.reason}'")
        setattr(obj, "username", username)

    return obj



