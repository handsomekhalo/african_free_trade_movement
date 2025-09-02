"""Urls for the api views of system_management app"""
from django.urls import path
import system_management.api.views as views
from system_management.api.api_helpers import send_email_api



urlpatterns = [

    # path('register_api/', views.register_api, name='register_api'),
    path('login_api/', views.login_api, name="login_api"),
    # path('get_users_api/', views.get_users_api, name="get_users_api"),
    # path('get_user_types_api/', views.get_user_types_api, name="get_user_types_api"),
    # path('update_user_api/', views.update_user_api, name="update_user_api"),
    # path('create_users_api/', views.create_users_api, name="create_users_api"),

    # path('logout_api/', views.logout_api, name="logout_api"),
    # path('send_email_api/', send_email_api, name='send_email_api'),
    # path('delete_user_api/', views.delete_user_api, name='delete_user_api'),


]
