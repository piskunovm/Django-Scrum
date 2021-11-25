import re
from html.parser import HTMLParser

from autoslug import AutoSlugField
from autoslug.settings import slugify as default_slugify
from django.db import models

from authapp.models import User


def replace_for_slug(value):
    return default_slugify(value).replace("-", "_")


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Category(models.Model):
    name = models.CharField(verbose_name="Название категории", max_length=64, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлено", auto_now=True)
    slug = AutoSlugField(populate_from="name", unique=True, slugify=replace_for_slug)

    class Meta:
        verbose_name = "Категории (Хабы)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"


class Article(models.Model):
    class StatusModel(models.TextChoices):
        draft = "draft"
        published = "published"
        moderation = "moderation"
        correction = "correction"
        archive = "archive"
        inactive = "inactive"

    status = models.CharField(
        max_length=16,
        choices=StatusModel.choices,
        default=StatusModel.draft,
    )

    title = models.TextField(verbose_name="Заголовок", max_length=256, blank=False, null=False)
    title_for_search = models.TextField(verbose_name="Заголовок", max_length=256, blank=False, null=False)
    preview = models.TextField(
        verbose_name="Предпросмотр статьи, краткое описание (до 512 символов)", max_length=512, blank=False, null=False
    )
    preview_for_search = models.TextField(
        verbose_name="Предпросмотр статьи, краткое описание (до 512 символов)", max_length=512, blank=False, null=False
    )
    body = models.TextField(verbose_name="Текст статьи", blank=False, null=False)
    body_for_search = models.TextField(verbose_name="Текст статьи", blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    image = models.ImageField(verbose_name="изображение", upload_to="article_images", blank=True)
    category = models.ForeignKey(
        Category, verbose_name="Категория/ХАБ", on_delete=models.CASCADE, related_name="articles"
    )
    tag = models.TextField(verbose_name="Теги", max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлено", auto_now=True)
    published_at = models.DateTimeField(verbose_name="Опубликованно", blank=True, null=True)

    # Поле, запоминающее количество комментариев под постом
    comments_count = models.PositiveIntegerField(verbose_name="Количество комментариев", default=0)
    count_of_likes = models.IntegerField(verbose_name="Число лайков", default=0)

    comment_moderator = models.TextField(verbose_name="Комментарий модератора", max_length=512, null=True)
    moderator_id = models.PositiveIntegerField(verbose_name="Модератор_id", blank=True, null=True)
    count_of_dislikes = models.IntegerField(verbose_name="Число дизлайков", default=0)
    rating = models.IntegerField(verbose_name="Рейтинг", default=0)
    audio_name = models.TextField(verbose_name="Имя аудио",
                                  max_length=32, blank=True)

    def get_count_post_likes(self):
        return Score.objects.filter(article_id=self.id, score="like").count()

    def get_count_post_dislikes(self):
        return Score.objects.filter(article_id=self.id, score="dislike").count()

    class Meta:
        verbose_name = "Посты"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.category} - {self.title}"

    @classmethod
    def get_articles_by_user(cls, user_pk):
        return cls.objects.filter(author_id=user_pk).all()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.title_for_search = self.title.lower()
        self.preview_for_search = self.preview.lower()
        self.body_for_search = strip_tags(self.body).lower()
        self.body_for_search = re.sub(" ", " ", self.body_for_search)
        super(Article, self).save()


# Таблица комментариев.
class Comments(models.Model):
    LIKE = 1
    NOTLIKE = 0

    # Столбец связи с пользователем.
    author_comment = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment", null=False, blank=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comment", null=False, blank=False)
    """id parent comment"""
    main_parent = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="another_replies", on_delete=models.CASCADE)
    # Столбец текста комментария.
    comment_text = models.TextField(
        max_length=400,
        blank=False,
        verbose_name="Написать комментарий",
    )
    comment_text_for_search = models.TextField(
        max_length=400,
        blank=False,
        verbose_name="Написать комментарий",
    )
    # Столбец даты создания комментария

    created_at = models.DateTimeField(verbose_name="Дата создания", editable=False, auto_now_add=True)
    # Столбец даты редактирования комментария
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)

    visibility = models.PositiveIntegerField(verbose_name="отображать комментарий", blank=False, null=False, default=1)

    class Meta:
        verbose_name = "Комментарии"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.id}, {self.author_comment}, {self.article}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.comment_text_for_search = strip_tags(self.comment_text).lower()
        self.comment_text_for_search = re.sub(" ", " ", self.comment_text_for_search)
        super(Comments, self).save()

    def delete(self, using=None, keep_parents=False):
        self.visibility = 0
        self.save()

    def get_count_comment_likes(self):
        return Score.objects.filter(comment_id=self.id, score="like").count()

    def get_count_comment_dislikes(self):
        return Score.objects.filter(comment_id=self.id, score="dislike").count()


class Score(models.Model):
    class StatusModel(models.TextChoices):
        like = "like"
        dislike = "dislike"

    score = models.CharField(max_length=16, choices=StatusModel.choices)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")

    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name="article", blank=True, null=True)

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name="comment1", blank=True, null=True)

    score_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="score_users", blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)



class Complaint(models.Model):
    """Модель содержащая жалобы пользователей на статьи и комментарии"""

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name="comment_id", null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="article_id", blank=True, null=True)
    # кто подал жалобу
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_user")
    complaint_text = models.TextField(verbose_name="Суть жалобы", max_length=256, blank=False, null=False)
    status = models.TextField(verbose_name="Жалоба активна", max_length=256, default="active")
    moderator_comment = models.TextField(verbose_name="Комментарий модератора", max_length=256, blank=False)
    moderator_id = models.PositiveIntegerField(verbose_name="Id_модератора", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Жалобы"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.article},{self.comment}  - {self.moderator_comment}"


class UserBan(models.Model):
    """Модель содержащая данные по банам пользователей"""

    # кто забанен
    banned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="banned_user")
    reason = models.TextField(verbose_name="Причина", max_length=256, blank=False, null=False)
    moderator_comment = models.TextField(verbose_name="Комментарий модератора", max_length=256, blank=True)
    moderator_id = models.PositiveIntegerField(verbose_name="Id_модератора", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Создано", editable=False, auto_now_add=True)
    ban_end_time = models.DateTimeField(verbose_name="Дата окончания бана", blank=False, null=False)

    class Meta:
        verbose_name = "Бан"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.banned_user},{self.reason}"
