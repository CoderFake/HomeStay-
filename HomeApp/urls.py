from django.urls import path
from .views import HomeAppView

urlpatterns = [
    path('', HomeAppView.as_view(), name='index'),
]