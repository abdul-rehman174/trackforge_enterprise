from django.urls import path
from . import views

urlpatterns = [
    path('stock_list/', views.stock_list, name='stock_list'),
    path('add_stock/', views.add_stock, name='add_stock'),
    path('update_stock/<int:pk>/', views.update_stock, name='update_stock'),
    path('delete_stock/<int:pk>/', views.delete_stock, name='delete_stock'),
]
