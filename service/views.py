from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils.timezone import now
from rest_framework_simplejwt.views import TokenObtainPairView
# djangorestframework-simplejwt

# import jwt

from django.conf import settings
from .serializers import UserCreateSerializer
from .models import (
    User, Role,
    Propriete, Unite,
    Tenant, Lease,
    Invoice, Paiement, Maintenance
)
from .serializers import (
    UserSerializer, RoleSerializer,
    ProprieteSerializer, UniteSerializer,
    TenantSerializer, BailSerializer,
    InvoiceSerializer, PaiementSerializer, MaintenanceSerializer, UserLoginSerializer
)



#==========================
#ROLES
#==========================
class RoleCreateView(generics.CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer




# =========================
# USERS
# =========================


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserList(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=204)

# login user jwt

class LoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer
# =========================
# ROLES
# =========================

class RoleList(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


# =========================
# PROPRIETES
# =========================


class ProprieteList(generics.CreateAPIView):
    queryset = Propriete.objects.all()
    serializer_class = ProprieteSerializer
class ProprieteDetail(APIView):
    def get(self, request, pk):
        propriete = get_object_or_404(Unite, pk=pk)
        serializer = UniteSerializer(propriete)
        return Response(serializer.data)

class ProprieteDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            propriete = Propriete.objects.get(pk=pk)
        except Propriete.DoesNotExist:
            return Response({"error": "Propriété non trouvée"},status=status.HTTP_404_NOT_FOUND)
        propriete.delete()
        return Response({"message": "Propriété supprimée avec succès"},status=status.HTTP_204_NO_CONTENT)

class ProprieteUpdateAPIView(APIView):

    def put(self, request, pk):
        try:
            propriete = Propriete.objects.get(pk=pk)
        except Propriete.DoesNotExist:
            return Response(
                {"error": "Propriété non trouvée"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProprieteSerializer(propriete,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProprietePartialUpdateAPIView(APIView):
    def patch(self, request, pk):
        try:
            propriete = Propriete.objects.get(pk=pk)
        except Propriete.DoesNotExist:
            return Response({"error": "Propriété non trouvée"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProprieteSerializer(propriete,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class TotalProprieteView(APIView):
    def get(self, request):
        return Response({'total_proprietes': Propriete.total_proprietes()})


# =========================
# UNITES
# =========================

class UnitListCreateView(generics.CreateAPIView):
    queryset = Unite.objects.all()
    serializer_class = UniteSerializer
    def get(self, request):
        unites = Unite.objects.all()
        serializer = UniteSerializer(unites, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UniteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UniteDetail(APIView):
    def get(self, request, pk):
        unite = get_object_or_404(Unite, pk=pk)
        serializer = UniteSerializer(unite)
        return Response(serializer.data)

class UniteUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            unite = Unite.objects.get(pk=pk)
        except Unite.DoesNotExist:
            return Response({"error": "unite non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UniteSerializer(unite, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnitePartialUpdateAPIView(APIView):

    def patch(self, request, pk):
        try:
            unite = Unite.objects.get(pk=pk)
        except Unite.DoesNotExist:
            return Response({"error": "Unite non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UniteSerializer(unite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniteDeleteAPIView(APIView):
    def delete(self, request, pk):
        unite = get_object_or_404(Unite, pk=pk)
        unite.delete()
        return Response({"message": "Unité supprimée avec succès"},status=status.HTTP_204_NO_CONTENT)

class OccupancyRateView(APIView):
    def get(self, request):
        occupancy_rate = Unite.occupancy_rate()
        return Response({'occupancy_rate':occupancy_rate})
# =========================
# Units Dashboard Stats
# =========================
class UnitDashboardView(APIView):
    def get(self, request):
        today = now().date()
        # Total unités
        total_units = Unite.objects.count()
        # Leases actifs (basé sur les dates)
        active_leases = Lease.objects.filter(date_start__lte=today).filter(date_end__isnull=True) | Lease.objects.filter(date_start__lte=today,date_end__gte=today)
        # Unités occupées
        occupied_units = Unite.objects.filter(id__in=active_leases.values_list("unit_id", flat=True)).distinct().count()
        # Unités vacantes
        vacant_units = total_units - occupied_units
        # Revenu total (loyer des unités occupées)
        total_revenue = active_leases.aggregate(total=Sum("monthly_rent"))["total"] or 0
        return Response({
            "total_units": total_units,
            "occupied_units": occupied_units,
            "vacant_units": vacant_units,
            "total_revenue": total_revenue
        })



# =========================
# TENANTS
# =========================

class TenantCreateView(generics.CreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class TenantList(APIView):
    def get(self, request):
        today = timezone.now().date()
        next_30_days = today + timedelta(days=30)
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        total_tenants = tenants.count()
        # Paiements à jour (payés aujourd’hui ou avant la date limite)
        current_payments = Paiement.objects.filter(payment_date__isnull=False,payment_date__lte=today).count()
        # Paiements en retard (date limite dépassée et non payés)
        late_payments = Paiement.objects.filter(payment_date__isnull=True,due_date__lt=today).count()
        # Baux expirant dans les 30 prochains jours
        expiring_leases = Lease.objects.filter(date_end__range=(today, next_30_days)).count()
        return Response({
            "total_tenants": total_tenants,
            "current_payments": current_payments,
            "late_payments": late_payments,
            "expiring_leases": expiring_leases,
            "tenants": serializer.data
        })


class TenantDetail(APIView):
    def get(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

class TenantUpdateAPIView(APIView):
    def put(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        serializer = TenantSerializer(tenant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TenantPartialUpdateAPIView(APIView):
    def patch(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        serializer = TenantSerializer(tenant,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class TenantDeleteAPIView(APIView):
    def delete(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        tenant.delete()
        return Response({"message": "Tenant supprimé avec succès"},status=status.HTTP_204_NO_CONTENT)



# =========================
# LEASE / BAIL
# =========================


# ------------------------------------
# LISTE + CRÉATION DES BAUX
# ------------------------------------
class BailListCreateView(generics.ListCreateAPIView):
    queryset = Lease.objects.all()
    serializer_class = BailSerializer

class BailDetail(APIView):
    def get(self, request, pk):
        bail = get_object_or_404(Lease, pk=pk)
        serializer = BailSerializer(bail)
        return Response(serializer.data)

class BailUpdateAPIView(APIView):

    def put(self, request, pk):
        bail = get_object_or_404(Lease, pk=pk)
        serializer = TenantSerializer(bail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BailPartialUpdateAPIView(APIView):
    def patch(self, request, pk):
        bail = get_object_or_404(Lease, pk=pk)
        serializer = TenantSerializer(bail,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class BailDeleteAPIView(APIView):
    def delete(self, request, pk):
        bail = get_object_or_404(Tenant, pk=pk)
        bail.delete()
        return Response({"message": "Bail supprimé avec succès"},status=status.HTTP_204_NO_CONTENT)
#------------------------------------
# DASHBOARD BAUX
# ------------------------------------
class BailDashboardView(APIView):
    def get(self, request):
        active_bails = Lease.active_leases()
        expiring_soon = Lease.expiring_soon(days=60)
        upcoming_bails = Lease.upcoming_leases()
        return Response({"total_bails": Lease.total_bails(), "active_leases":
            {"count": active_bails.count(),
             },"expiring_soon": {"count": expiring_soon.count(),
            },"upcoming_leases": {"count": upcoming_bails.count(),
            },"total_monthly_revenue": Lease.total_monthly_revenue()
        }, status=status.HTTP_200_OK)


# =========================
# INVOICES
# =========================

# ------------------------------------
# LISTE + CRÉATION DES FACTURES
# ------------------------------------
class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class InvoiceDetail(APIView):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        serializer = BailSerializer(invoice)
        return Response(serializer.data)


class InvoiceUpdateAPIView(APIView):
    def put(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        serializer = TenantSerializer(invoice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class InvoicePartialUpdateAPIView(APIView):
    def patch(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        serializer = TenantSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDeleteAPIView(APIView):
    def delete(self, request, pk):
        invoice = get_object_or_404(Tenant, pk=pk)
        invoice.delete()
        return Response({"message": "Invoice supprimé avec succès"}, status=status.HTTP_204_NO_CONTENT)
# ------------------------------------
# DASHBOARD FACTURES
# ------------------------------------
class InvoiceDashboardView(APIView):
    def get(self, request):
        invoices = Invoice.objects.all()
        return Response({
            "total_invoiced": Invoice.total_invoices(),      # FCFA
            "paid": Invoice.total_paid(),                    # FCFA
            "pending": Invoice.total_pending(),              # FCFA
            "overdue": Invoice.total_overdue(),              # FCFA

            "invoices": InvoiceSerializer(invoices, many=True).data}, status=status.HTTP_200_OK)


# =========================
# PAYMENTS
# =========================



class PaiementListCreateView(generics.ListCreateAPIView):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

class PaiementDetail(APIView):
    def get(self, request, pk):
        paiement = get_object_or_404(Paiement, pk=pk)
        serializer = PaiementSerializer(paiement)
        return Response(serializer.data)

class PaiementUpdateAPIView(APIView):
    def put(self, request, pk):
        paiement = get_object_or_404(Paiement, pk=pk)
        serializer = PaiementSerializer(paiement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PaiementPartialUpdateAPIView(APIView):
    def patch(self, request, pk):
        paiement = get_object_or_404(Paiement, pk=pk)
        serializer = PaiementSerializer(paiement,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class PaiementDeleteAPIView(APIView):
    def delete(self, request, pk):
        paiement = get_object_or_404(Paiement, pk=pk)
        paiement.delete()
        return Response({"message": "Paiement supprimé avec succès"},status=status.HTTP_204_NO_CONTENT)

class PaiementDashboardView(APIView):

    def get(self, request):
        return Response({
            "total_received": Paiement.total_received(),
            "completed": Paiement.total_paid(),
            "pending": Paiement.total_pending(),
            "late": Paiement.total_late(),
            "collection_rate": Paiement.collection_rate()
        }, status=status.HTTP_200_OK)

class NombrePaiementsView(APIView):
    def get(self, request):
        return Response({
            "nombre_paiements": Paiement.nombre_paiements()
        })
#======================
#maintenanceViews
#=========================

# CREATE + LIST
class MaintenanceListCreateView(generics.ListCreateAPIView):
    queryset = Maintenance.objects.all().order_by("-created_at")
    serializer_class = MaintenanceSerializer

# RETRIEVE + UPDATE + DELETE
class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    def active_maintenance_count(self):
        return Maintenance.objects.exclude(
            status__in=["resolved", "closed"]
        ).count()
    def maintenance_by_unit(unit_id):
        return Maintenance.objects.filter(unit_id=unit_id)

class TotalMaintenanceView(APIView):
    def get(self, request):
        return Response({'total_maintenance': Maintenance.total_maintenance()})


