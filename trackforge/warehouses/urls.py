from django.urls import path
from . import views

urlpatterns = [
    path('warehouse_list/', views.warehouse_list, name='warehouse_list'),
    path('add_warehouse/', views.add_warehouse, name='add_warehouse'),
    path('update_warehouse/<int:pk>/', views.update_warehouse, name='update_warehouse'),
    path('delete_warehouse/<int:pk>/', views.delete_warehouse, name='delete_warehouse'),
]
