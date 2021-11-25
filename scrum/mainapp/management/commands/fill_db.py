import copy
import datetime
import json
import os
import random
import shutil
import threading
import time
from sys import platform

import pytz
from django.conf import settings
from django.core.files import File
from django.core.management import BaseCommand
from post_office.models import EmailTemplate

from authapp.models import User
from lkapp.helpers.alerts.alert import SaveAlert
from lkapp.helpers.rating_author import author_rate_up_before_publicated
from lkapp.models import UserSettings
from mainapp.helpers.post_rate import rating
from mainapp.models import Article, Category, Comments, Score
from scrum.settings import ARTICLE_AUDIO_ROOT


def load_from_json(file_name):
    return json.load(
        open(os.path.join(settings.JSON_PATH, f'fill_db', f'{file_name}.json'),
             encoding='utf-8'))


def create_db():
    print('Создание и применение миграций...')
    if platform == "win32":
        os.system("py manage.py flush --no-input")
        os.system("py manage.py makemigrations")
        os.system("py manage.py migrate")
    else:
        os.system("python3 manage.py flush --no-input")
        os.system("python3 manage.py makemigrations")
        os.system("python3 manage.py migrate")


def load_email_template():
    print('Загрузка рейтинга...')
    EmailTemplate.objects.all().delete()
    email_templates = load_from_json('post_office_emailtemplate')
    for email_template in email_templates:
        EmailTemplate.objects.create(**email_template)


def load_users():
    print('Загрузка пользователей...')
    User.objects.all().delete()
    users = load_from_json('users')

    for _user in users:
        if _user['superuser']:
            _user.pop("superuser")
            user = User.objects.create_superuser(**_user)
        else:
            _user.pop("superuser")
            user = User.objects.create_user(**_user)
        UserSettings.objects.create(user=user)


def load_categories():
    print('Загрузка категорий...')
    Category.objects.all().delete()
    categories = load_from_json('categories')
    for category in categories:
        Category.objects.create(name=category)


def load_articles():
    print('Загрузка постов...')
    Article.objects.all().delete()
    articles = load_from_json('articles')

    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              f'{settings.MEDIA_ROOT}', 'article_images')
    if os.path.exists(image_path):
        shutil.rmtree(image_path)

    for article in articles:
        image = article['image']
        article.pop('image')
        article['author'] = User.objects.get(username=article['author'])
        article['category'] = Category.objects.get(name=article['category'])
        if article['moderator_id']:
            moderator = User.objects.get(username=article['moderator_id'])
            article['moderator_id'] = moderator.pk
        else:
            article.pop('moderator_id')
        if article['published_at']:
            article['published_at'] = datetime.datetime.strptime(
                article['published_at'], '%d.%m.%y %H:%M:%S')
            tz = pytz.timezone('UTC')
            article['published_at'] = tz.localize(article['published_at'])

        else:
            article.pop('published_at')

        _article = Article.objects.create(**article)
        if _article.status == 'published':
            author_rate_up_before_publicated(_article.author_id)

        try:
            _article.image.save(f'{image}',
                                File(open(os.path.join(
                                    f'{settings.JSON_IMAGE_PATH}', 'fill_db',
                                    f'{image}'), 'rb')))
            _article.save()
        except Exception:
            pass


def load_comments():
    print('Загрузка комментариев...')
    Comments.objects.all().delete()

    articles = Article.objects.filter(status='published').all()
    users = User.objects.all()

    comments = load_from_json('comments')
    # ic(comments)
    comments_to_comments = load_from_json('comments_to_comments')

    for article in articles:
        user_id_list = [i for i in range(1, users.count() + 1)]
        _comments = copy.deepcopy(comments)
        n_of_comments = random.randrange(2, users.count())
        for i in range(n_of_comments):
            user_id = user_id_list.pop(random.randrange(len(user_id_list)))
            user = users.get(pk=user_id)
            comment = _comments.pop(random.randrange(len(_comments)))
            new_comment = Comments.objects.create(author_comment=user,
                                                  article=article,
                                                  comment_text=comment['text'],
                                                  )
            SaveAlert(action_user=user, post=article,
                      comment=new_comment, event_type="comment")
            article.comments_count += 1

        article.save()

    comments = Comments.objects.all()
    comment_id_list = [i for i in range(1, comments.count() + 1)]
    n_of_comments_to_comment = random.randrange(comments.count() // 2,
                                                comments.count())
    for i in range(n_of_comments_to_comment):
        user = users.get(pk=random.randrange(1, users.count() + 1))
        comment_to_comment = comments_to_comments[
            random.randrange(len(comments_to_comments))]
        comment = comments.get(
            pk=comment_id_list.pop(random.randrange(len(comment_id_list))))
        article = comment.article
        Comments.objects.create(author_comment=user,
                                main_parent=comment,
                                article=article,
                                comment_text=comment_to_comment['text'],
                                )


def load_likes_and_dislikes():
    from mainapp.helpers.scores.score_author import to_score
    from mainapp.helpers.scores.score_post import to_score_post
    from mainapp.helpers.scores.score_comment import to_score_comment
    print('Загрузка лайков и дизлайков...')
    Score.objects.all().delete()
    # Dislike.objects.all().delete()

    articles = Article.objects.all()
    comments = Comments.objects.all()
    users = User.objects.all()

    for _user in users:
        user_id_list = [i for i in range(1, users.count() + 1)]
        n_of_likes = random.randrange(2, users.count())
        for i in range(n_of_likes):
            user_id = user_id_list.pop(random.randrange(len(user_id_list)))
            if user_id == _user.id:
                continue
            user = users.get(pk=user_id)
            to_score(user, _user, "like")
        for user_id in user_id_list:
            if user_id == _user.id:
                continue
            user = users.get(pk=user_id)
            to_score(user, _user, "dislike")

    for article in articles:
        user_id_list = [i for i in range(1, users.count() + 1)]
        n_of_likes = random.randrange(2, users.count())
        for i in range(n_of_likes):
            user_id = user_id_list.pop(random.randrange(len(user_id_list)))
            user = users.get(pk=user_id)
            to_score_post(user, article.id, "like")
        for user_id in user_id_list:
            user = users.get(pk=user_id)
            to_score_post(user, article.id, "dislike")

    for comment in comments:
        user_id_list = [i for i in range(1, users.count() + 1)]
        n_of_likes = random.randrange(2, users.count())
        for i in range(n_of_likes):
            user_id = user_id_list.pop(random.randrange(len(user_id_list)))
            user = users.get(pk=user_id)
            to_score_comment(user, comment.id, "like")
        for user_id in user_id_list:
            user = users.get(pk=user_id)
            to_score_comment(user, comment.id, "dislike")


def load_rating():
    print('Загрузка рейтинга...')
    articles = Article.objects.all()
    for article in articles:
        rating(article)


def load_audio():
    print('Формирование аудиодорожек...')
    count_thr = threading.active_count()
    articles = Article.objects.all()
    if os.path.exists(ARTICLE_AUDIO_ROOT):
        shutil.rmtree(ARTICLE_AUDIO_ROOT)
    for article in articles:
        if article.status == 'published':
            from mainapp.helpers.article.article_audio import generate_article_audio
            generate_article_audio(article)

    current_count_thr = threading.active_count()
    print(f'....Осталось аудиодорожек - {threading.active_count() - count_thr}')
    while True:
        time.sleep(1)
        if current_count_thr > threading.active_count():
            current_count_thr = threading.active_count()
            print(f'....Осталось аудиодорожек - {threading.active_count() - count_thr}')
        if threading.active_count() == count_thr:
            break


def load_followers():
    print('Загрузка подписчиков...')
    users = User.objects.all()

    for _user in users:
        user_id_list = [i for i in range(1, users.count() + 1)]
        n_of_followers = random.randrange(2, users.count())
        for i in range(n_of_followers):
            user_id = user_id_list.pop(random.randrange(len(user_id_list)))
            if user_id == _user.id:
                continue
            user = users.get(pk=user_id)
            user.follows.add(_user)
            _user.followers.add(user)
            SaveAlert(action_user=user, alert_user=_user,
                      event_type="author_subscribe")


class Command(BaseCommand):
    def handle(self, *args, **options):
        settings.SEND_EMAIL = False
        generate_audio = input('Для того, чтобы сформировать аудиодорожки введите "да" - ')
        create_db()
        load_email_template()
        load_users()
        load_categories()
        load_articles()
        load_comments()
        load_likes_and_dislikes()
        load_followers()
        load_rating()

        if generate_audio == "да":
            load_audio()
        settings.SEND_EMAIL = True
        print('Загрузка данных завершена.')
