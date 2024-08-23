# from django.urls import reverse
# from rest_framework.exceptions import NotAuthenticated
#
#
# class HandleErrorMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#
#         if response.status_code == 404 and request.path.startswith('/static/'):
#             return response
#
#         if response.status_code == 401:
#             response = reverse('login')
#
#         elif isinstance(response, NotAuthenticated):
#             response = reverse('login')
#
#         return response
#
#     def process_exception(self, request, exception):
#         if isinstance(exception, NotAuthenticated):
#             response = reverse('login')
#         else:
#             response = reverse('not_found')
#         return response
