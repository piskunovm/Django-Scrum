"""scrum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import (
    main,
    read_post,
    hubs,
    like_post,
    dislike_post,
    comments_count,
    allert_counter,
    profile_page,
    follow,
    like_author,
    dislike_author,
    post_complaint,
    comment_complaint,
    search, get_audio_name, get_audio_block,
    set_user_ban_status,
    set_user_unban_status, like_comment, dislike_comment, comment_ajax,like_dislike_comment_ajax, regenerate_audio
)

app_name = "mainapp"

urlpatterns = [
    # Страница автора
    path("user/<int:pk>", profile_page, name="profile_page"),

    # Оценка автора
    path("user/like/<int:pk>", like_author, name="like_author"),
    path("user/dislike/<int:pk>", dislike_author, name="dislike_author"),

    # Оценка автора (ajax)
    path("user/like/<int:pk>/like_user_count",
         like_author, name="like_author_ajax"),
    path("user/dislike/<int:pk>/dislike_user_count",
         dislike_author, name="dislike_author_ajax"),

    # Подписка
    path("user/follow/<int:pk>", follow, name="follow"),

    # Главная + страницы Хабов + сортировка
    path("", main, name="index"),
    path("index/<str:sorted_by>/", main, name="index_sorted"),
    path("category/<slug:slug>/", hubs, name="category"),
    path("index/<slug:slug>/<str:sorted_by>/", hubs, name="category_sorted"),

    # Страница статьи
    path("post/<int:pk>/", read_post, name="read_post"),

    # Оценка статьи
    path("post/<int:pk>/like_count", like_post, name="like_count"),
    path("post/<int:pk>/dislike_count", dislike_post, name="dislike_count"),

    # Комментарии
    path("post/<int:pk>/comments_count", comments_count, name="comments_count"),
    path("post/<int:pk>/get_comment", comment_ajax, name="get_comment"),
    path("post/<int:pk>/like_dislike_comment", like_dislike_comment_ajax, name="like_dislike_comment"),    

    # Жалоба на комментарий
    path("post/<int:pk>/comment_complaint",
         comment_complaint, name="comment_complaint"),

    # Оценка комментария
    path("post/<int:pk>/like_comment", like_comment, name="like_comment"),
    path("post/<int:pk>/dislike_comment", dislike_comment, name="dislike_comment"),


    # Счетчик уведомлений
    path("post/allert_counter", allert_counter, name="allert_counter"),

    # Поиск
    path("post/<int:pk>/post_complaint", post_complaint, name="post_complaint"),
    path("search/", search, name="search"),

    # Аудио
    path("media/article_audio/<str:audio_name>/", get_audio_name, name="get_audio_name"),
    path("post/get_audio_block/", get_audio_block, name="get_audio_block"),
    path("post/regenerate_audio/", regenerate_audio, name="regenerate_audio"),
    
    # Бан
    path("user/ban/", set_user_ban_status,
         name="set_user_ban_status"),
    path("user/<int:pk>/unban/", set_user_unban_status,
         name="set_user_unban_status"),
]
