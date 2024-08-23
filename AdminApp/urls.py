from django.urls import path
from .views import (DashboardView, PermissionsView, UserListView,
                    UserAdminView, UserProfileView, UserView,
                    HomestayAdminView, HomestayListView, HomestayCreateUpdateView)

urlpatterns = [
    path('', DashboardView.as_view(), name='admin'),
    path('permissions/', PermissionsView.as_view(), name='permissions'),

    #user
    path('user-manager/', UserAdminView.as_view(), name='user_manager'),
    path('profile-user/', UserProfileView.as_view(), name='profile_user'),

    path('user-list/', UserListView.as_view(), name='user_list'),
    path('edit-user/', UserView.as_view(), name='edit_user'),

    #homestay
    path('homestay-manager/', HomestayAdminView.as_view(), name='homestay_manager'),

    path('homestay-list/', HomestayListView.as_view(), name='homestay_list'),
    path('homestay-create-update/', HomestayCreateUpdateView.as_view(), name='homestay_create_update_delete')
]