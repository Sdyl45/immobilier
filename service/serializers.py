from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import (
    Role,
    User,
    Propriete,
    Unite,
    Tenant,
    Lease,
    Invoice,
    Paiement, Maintenance
)

# =========================
# ROLE
# =========================
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id',)


# =========================
# USER (CUSTOM)
# =========================
class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'role',
            'password',
        )
        read_only_fields = ('id', 'date_joined')

# serializer for create user
class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
            'role',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# serializer for login user
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajoutez des champs personnalisés au token si nécessaire
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Ajoutez des informations supplémentaires sur l'utilisateur si nécessaire
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role.name if self.user.role else None,
        }
        return data

# =========================
# PROPRIETE
# =========================
class ProprieteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propriete
        fields = '__all__'
        read_only_fields = ('id', 'purchase_date')


# =========================
# UNITE
# =========================
class UniteSerializer(serializers.ModelSerializer):
    propriete = serializers.PrimaryKeyRelatedField(
        queryset=Propriete.objects.all(),
        required=True
    )

    class Meta:
        model = Unite
        fields = '__all__'
        read_only_fields = ('id',)


# =========================
# TENANT
# =========================
class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ('id', 'date_creation', 'date_naissance')


# =========================
# LEASE / BAIL
# =========================
class BailSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all(),required=True)
    id_property = serializers.PrimaryKeyRelatedField(queryset=Propriete.objects.all(),required=True)
    unit = serializers.PrimaryKeyRelatedField(queryset=Unite.objects.all(),required=True)
    monthly_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    security_deposit = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    payment_frequency = serializers.CharField(required=True)
    payment_due_date = serializers.IntegerField(required=True)

    class Meta:
        model = Lease
        fields = "__all__"
        read_only_fields = ("id","id")


# =========================
# INVOICE
# =========================
class InvoiceSerializer(serializers.ModelSerializer):
    id_lease = serializers.PrimaryKeyRelatedField(
        queryset=Lease.objects.all(),
        required=True
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('id', 'date')


# =========================
# PAIEMENT
# =========================
class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = (
            "__all__"
        )
        read_only_fields = ("id", "payment_date")



#======================
#maintenanceSerializers
#=======================


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = "__all__"