from django.urls import path
from . import views

urlpatterns = [
    # Supplier URLs
    path('supplier_list/', views.supplier_list, name='supplier_list'),
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('update_supplier/<int:pk>/', views.update_supplier, name='update_supplier'),
    path('delete_supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),

#     # Purchase Order URLs
    path('purchaseorder_list/', views.purchaseorder_list, name='purchaseorder_list'),
    path('add_purchaseorder/', views.add_po, name='add_purchsalorder'),
    path('purchaseorder/<int:pk>/', views.po_detail, name='po_detail'),

    path('purchaseorder/<int:pk>/update-status/', views.update_po_status, name='update_po_status'),
    # path('purchaseorder/<int:pk>/submit/', views.submit_po, name='submit_po'),
    # path('purchaseorder/<int:pk>/receive/', views.receive_po, name='receive_po'),
    # path('purchaseorder/<int:pk>/cancel/', views.cancel_po, name='cancel_po'),

]