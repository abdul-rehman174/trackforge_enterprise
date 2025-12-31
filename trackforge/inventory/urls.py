from django.urls import path
from .views import *

urlpatterns = [
    path("product_list/", product_list, name="product_list"),
    path("add_product/", add_product, name="add_product"),
    path("update_product/<int:pk>/", update_product, name="update_product"),
    path("delete_product/<int:pk>/", delete_product, name="delete_product"),

    # --- 2. CATEGORY  ---
    path('categories/', category_list, name='category_list'),
    path('categories/add/', category_create, name='category_create'),
    path('categories/edit/<int:pk>/', category_update, name='category_update'),
    path('categories/delete/<int:pk>/', category_delete, name='category_delete'),

    # --- 3. WAREHOUSE  ---
    path('warehouses/', warehouse_list, name='warehouse_list'),
    path('warehouses/add/', warehouse_create, name='warehouse_create'),
    path('warehouses/edit/<int:pk>/', warehouse_update, name='warehouse_update'),
    path('warehouses/delete/<int:pk>/', warehouse_delete, name='warehouse_delete'),
    # --4. Stock  ---
    path('stock/', stock_list, name='stock_list'),
    # --- 5. Transaction  ---
    path('transaction_history/', transaction_history, name='transaction_history'),



]