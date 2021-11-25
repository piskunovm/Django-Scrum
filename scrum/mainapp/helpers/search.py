from django.db.models import Q
from django.template.loader import render_to_string

from authapp.models import User
from mainapp.models import Comments, Article


def get_search_results(search_request, filter, order_by=None):
    if filter == "posts":
        search_result = Article.objects.filter(
            Q(status="published")
            & (
                    Q(title_for_search__icontains=search_request)
                    | Q(preview_for_search__icontains=search_request)
                    | Q(body_for_search__icontains=search_request)
            )
        )
    elif filter == "comments":
        search_result = Comments.objects.filter(Q(comment_text__icontains=search_request))
        # for item in search_result:
        #     print(item.comment_text)
    elif filter == "users":
        search_result = User.objects.filter(
            Q(is_active=True)
            & (
                    Q(username__icontains=search_request)
                    | Q(first_name__icontains=search_request)
                    | Q(last_name__icontains=search_request)
            )
        )
    else:
        search_result = None
    return search_result


def perform_search(search_request, filter, content, is_ajax=False, order_by=None):
    if is_ajax:
        template = "mainapp/includes/inc__search_not_found.html"
        if len(search_request) > 0:
            search_results = get_search_results(search_request, filter)
            if search_results:
                content[filter] = search_results
                if filter == "posts":
                    template = "mainapp/includes/inc__articles_list.html"
                elif filter == "comments":
                    template = "mainapp/includes/inc__search_comments_list.html"
                elif filter == "users":
                    template = "mainapp/includes/inc__search_users_list.html"
            else:
                content["filter"] = filter
            return render_to_string(template, content)
        else:
            content["filter"] = filter
            return render_to_string(template, content)
    else:
        return get_search_results(search_request, filter)
