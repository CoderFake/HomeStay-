
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500
from api.views import bad_request_view, not_found_view

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("admin/", include("AdminApp.urls")),
    path("", include("HomeApp.urls")),
    path("accounts/", include("Accounts.urls")),
    path("homestays/", include("Homestays.urls")),
    path("orders/", include("Orders.urls")),
    path("errors/", include("api.urls"))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

#
# handler400 = 'api.views.bad_request_view'
# handler404 = 'api.views.not_found_view'
