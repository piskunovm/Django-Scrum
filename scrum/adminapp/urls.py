from django.urls import path

import adminapp.views as adminapp

app_name = "adminapp"

urlpatterns = [
    # path("", adminapp.index, name="index"),
    path("users/", adminapp.get_users, name="get_users"),
    path("users/delete/<int:pk>/", adminapp.change_user_status,
         name="change_user_status"),
    path("users/role/<int:pk>/<str:role>/", adminapp.change_user_role,
         name="change_user_role"),
    path("users/create/", adminapp.create_user, name="create_user"),
    path("users/get/<int:pk>/", adminapp.get_user_info, name="get_user"),
    # path("categories/", adminapp.get_categories, name="get_categories"),
    # path("posts/", adminapp.get_posts, name="get_posts"),
    path("search/", adminapp.search_ajax, name="search_ajax"),
]
