"""
URL configuration for inventory_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from inventory.views import OnHandBalanceReportView, FetchOnHandBalanceReportView, ProjectedObsolescenceView, CycleCountView, CarryingCostView, InventoryOutstandingView,PaidInvoicesView, get_boldbi_url, CpoPaidInvoicesView, UploadInventoryDataView
# from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/users/', include('users.urls')), 
    path('onhand-balance-reports/', OnHandBalanceReportView.as_view(), name='upload-excel'),
    path('get-onhand-reports/', FetchOnHandBalanceReportView.as_view(), name='onhand-report'),
    path('projected-obsolescence/', ProjectedObsolescenceView.as_view(), name='projected-obsolescence'),
    path('get-projected-obsolescence/', ProjectedObsolescenceView.as_view(), name='projected-obsolescence-list'),
    path('cycle-counts-upload/', CycleCountView.as_view(), name='cycle-counts-upload'),
    path('cycle-counts/', CycleCountView.as_view(), name='cycle-count-list'),
    path('carrying-cost-upload/', CarryingCostView.as_view(), name='cycle-counts-upload'),
    path('carrying-costs/', CarryingCostView.as_view(), name='cycle-counts-list'),
    path('inventory-outstanding-upload/', InventoryOutstandingView.as_view(), name='inventory-outstanding-upload'),
    path('inventory-outstandings/', InventoryOutstandingView.as_view(), name='inventory-outstandings-list'),
    path('paid-invoices-upload/', PaidInvoicesView.as_view(), name='paid-invoices-upload'),
    path('cpo-paid-invoices-upload/', CpoPaidInvoicesView.as_view(), name='cpo-paid-invoices-upload'),
    path('get-paid-invoices/', PaidInvoicesView.as_view(), name='paid-invoices-list'),
    path('proxy/boldbi-url/', get_boldbi_url, name='get_boldbi_url'),
    path('upload-inventory/', UploadInventoryDataView.as_view(), name='upload-inventory'),
    
]

