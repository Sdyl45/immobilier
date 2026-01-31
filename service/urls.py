from django.urls import path
from .views import *

urlpatterns = [

    # =========================
    # USERS & ROLES
    # =========================
    path('api/users/', UserList.as_view(), name='user_list'),
    path('api/users/create/', UserCreate.as_view(), name='user_create'),
    path('api/users/<int:pk>/', UserDetail.as_view(), name='user_detail'),

    path('api/roles/', RoleList.as_view(), name='role_list'),
    path('api/roles/create/', RoleCreateView.as_view(), name='role_create'),


    # =========================
    # PROPERTIES
    # =========================
    path('proprietes/', ProprieteList.as_view(), name='propriete_list'),
    path('proprietes/total/', TotalProprieteView.as_view(), name='total_propriete'),
    path('proprietes/detail/<int:pk>/', ProprieteDetail.as_view(), name='detail_propriete'),
    path("proprietes/delete/<int:pk>/", ProprieteDeleteAPIView.as_view()),
    path("proprietes/update/<int:pk>/", ProprieteUpdateAPIView.as_view()),
    path("proprietes/partial-update/<int:pk>/", ProprietePartialUpdateAPIView.as_view()),

    # =========================
    # UNITES
    # =========================
    path('unites/ListCreate/', UnitListCreateView.as_view(), name='unite_list'),
    path('unites/Dashboard/', UnitDashboardView.as_view(), name='unite_list'),
    path('unites/Details/<int:pk>/', UniteDetail.as_view(), name='unite_detail'),
    path("unites/Update/<int:pk>/", UniteUpdateAPIView.as_view()),
    path("unites/Partial/Update/<int:pk>/", UnitePartialUpdateAPIView.as_view()),
    path("unites/Delete/<int:pk>/", UniteDeleteAPIView.as_view()),

    # =========================
    # TENANTS
    # =========================
    path('tenantsDashboard/', TenantList.as_view(), name='tenant_list'),
    path('tenants/create/', TenantCreateView.as_view(), name='tenant_create'),
    path('tenantsDetails/<int:pk>/', TenantDetail.as_view(), name='tenant_detail'),
    path("tenantsUpdate/<int:pk>/", TenantUpdateAPIView.as_view(),name='tenant_update'),
    path("TenantPartialUpdate/<int:pk>/", TenantPartialUpdateAPIView.as_view()),
    path("tenantsDelete/<int:pk>/", TenantDeleteAPIView.as_view(),name='delete_tenant'),

    # =========================
    # LEASE / BAIL
    # =========================
    path('bails/', BailListCreateView.as_view(), name='bail_list'),
    path('BailDashboard/', BailDashboardView.as_view(), name='total_bail'),
    path('BailDetail/<int:pk>/', BailDetail.as_view(), name='detail_bail'),
    path('Bail/Update/<int:pk>/', BailUpdateAPIView.as_view(), name='Bail_Update'),
    path('Bail/Update/partial/<int:pk>/', BailPartialUpdateAPIView.as_view(), name='Bail_Update_partial'),
    path('Bail/Delete/<int:pk>/', BailDeleteAPIView.as_view(), name='Bail_Delete'),

    # =========================
    # INVOICES
    # =========================

    path('invoices/create/', InvoiceListCreateView.as_view(), name='invoice_create'),
    path('invoices/total/', InvoiceDashboardView.as_view(), name='total_invoice'),
    path('invoices/detail/<int:pk>/', InvoiceDetail.as_view(), name='detail_invoice'),
    path('invoices/update/<int:pk>/', InvoiceUpdateAPIView.as_view(), name='update_invoice'),
    path('invoices/update/partial/<int:pk>/', InvoicePartialUpdateAPIView.as_view(), name='partial_update_invoice'),
    path('invoices/delete/<int:pk>/', InvoiceDeleteAPIView.as_view(), name='delete_invoice'),

    # =========================
    # PAYMENTS
    # =========================

    path("paiements/", PaiementListCreateView.as_view(),name='paiement_create_list'),
    path("paiements/dashboard/", PaiementDashboardView.as_view(),name='paiement_stat'),
    path("paiements/count/", NombrePaiementsView.as_view(),name='paiement_count'),
    path("paiements/Detail/<int:pk>/", PaiementDetail.as_view(), name='paiement_Detail'),
    path("paiements/Update/<int:pk>/", PaiementUpdateAPIView.as_view(), name='paiement_Update'),
    path("paiements/PartialUpdate/<int:pk>/", PaiementPartialUpdateAPIView.as_view(), name='paiement_PartialUpdate'),
    path("paiements/Delete/<int:pk>/", PaiementDeleteAPIView.as_view(), name='paiement_Delete'),
    # =========================
    # maintenanceURl
    # =========================

    path("maintenanceList_Create/", MaintenanceListCreateView.as_view(), name="maintenance-list-create"),
    path("Total_maintenance/", TotalMaintenanceView.as_view(), name="maintenance-list-create"),
        path("maintenance/<int:pk>/", MaintenanceDetailView.as_view(), name="maintenance-detail"),
    path("OccupancyRate/", OccupancyRateView.as_view(), name="OccupancyRate-detail"),
]
