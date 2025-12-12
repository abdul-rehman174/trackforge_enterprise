
from django.contrib import admin
from django.urls import path,include
from .views import user_list , create_user,update_user,delete_user

urlpatterns = [
    path("user_list/",user_list, name="user_list"),
    path("create_user/",create_user,name="create_user"),
    path("update_user/<int:pk>/",update_user,name="update_user"),
    path("delete_user/<int:pk>/",delete_user,name="delete_user"),

]
