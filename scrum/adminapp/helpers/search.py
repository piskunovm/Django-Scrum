from django.db.models import Q
from django.template.loader import render_to_string

from authapp.models import User


def get_search_results(search_request, filter, order_by='pk'):
    if filter == "users":
        if search_request:
            search_result = User.objects.filter(
                Q(username__icontains=search_request)
                | Q(first_name__icontains=search_request)
                | Q(last_name__icontains=search_request)
                | Q(email__icontains=search_request)
            ).order_by(order_by)
        else:
            search_result = User.objects.all().order_by(order_by)
    else:
        search_result = None
    if len(search_result) == 0:
        search_result = None
    return search_result


def perform_search_ajax(search_request, filter, order_by=None):
    content = {
        'filter': filter,
    }
    template = "mainapp/includes/inc__search_not_found.html"
    search_results = get_search_results(search_request, filter)
    if search_results:
        if filter == "users":
            content['users'] = search_results
            template = "adminapp/includes/inc__admin_users_list.html"

    return render_to_string(template, content)
