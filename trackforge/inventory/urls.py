from django.urls import path
from .views import *

urlpatterns = [
    path("product_list",product_list,name="product_list"),
    path("add_product",add_product,name="add_product"),
    path("update_product/<int:pk>/",update_product,name="update_product"),
    path("delete_product/<int:pk>/",delete_product,name="delete_product"),


]