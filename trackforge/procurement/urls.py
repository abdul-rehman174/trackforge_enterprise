from django.urls import path
from . import views

urlpatterns = [
    # Supplier URLs
    path('supplier_list/', views.supplier_list, name='supplier_list'),
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('update_supplier/<int:pk>/', views.update_supplier, name='update_supplier'),
    path('delete_supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    # Purchase Order URLs
    path('purchaseorder_list/', views.purchaseorder_list, name='purchaseorder_list'),
    path('add_purchaseorder/', views.add_purchaseorder, name='add_purchaseorder'),
    path('update_purchaseorder/<int:pk>/', views.update_purchaseorder, name='update_purchaseorder'),
    path('delete_purchaseorder/<int:pk>/', views.delete_purchaseorder, name='delete_purchaseorder'),
]
