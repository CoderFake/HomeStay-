from django.urls import path
from .views import bad_request_view, not_found_view, GetLocationsView

urlpatterns = [
    path('bad-request/', bad_request_view, name='bad_request'),
    path('not-found/', not_found_view, name='not_found'),
    path('locations/', GetLocationsView.as_view(), name='locations')
]