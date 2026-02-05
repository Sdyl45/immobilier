# pharmacy_app/permissions.py
from rest_framework import permissions
from .models import Role

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to SuperAdmin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == Role.ADMINISTRATOR

class IsPropertyManager(permissions.BasePermission):
    """
    Allows access only to CompanyAdmin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == Role.PROPERTY_MANAGER

class IsMaintenanceStaff(permissions.BasePermission):
    """
    Allows access only to AgencyAdmin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == Role.MAINTENANCE_STAFF

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allows access only to the user themselves or to SuperAdmin/CompanyAdmin/AgencyAdmin.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for anyone authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow full access if the user is a SuperAdmin, CompanyAdmin, or AgencyAdmin
        if request.user.role in [Role.ADMINISTRATOR, Role.PROPERTY_MANAGER, Role.MAINTENANCE_STAFF]:
            return True

        # Allow access only if the user is the owner of the object
        return obj == request.user




class IsSuperAdminOrCompanyAdmin(permissions.BasePermission):
    """
    Allows access only to SuperAdmin or CompanyAdmin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]