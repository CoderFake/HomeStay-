from django.http import Http404, HttpResponseNotFound
from django.template.loader import render_to_string
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, Http404):
            content = render_to_string('not_found.html')
            return HttpResponseNotFound(content)

    return response
