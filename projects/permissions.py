from rest_framework import permissions
from .models import ProjectUser


class IsProjectOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a project to perform certain actions.
    """
    def has_object_permission(self, request, view, obj):
        try:
            return obj.projectuser_set.get(user=request.user).role == ProjectUser.OWNER
        except ProjectUser.DoesNotExist:
            return False


class IsProjectOwnerOrEditor(permissions.BasePermission):
    """
    Custom permission to allow owners and editors of a project to perform certain actions.
    """
    def has_object_permission(self, request, view, obj):
        try:
            role = obj.projectuser_set.get(user=request.user).role
            return role in [ProjectUser.OWNER, ProjectUser.EDITOR]
        except ProjectUser.DoesNotExist:
            return False


class HasProjectAccess(permissions.BasePermission):
    """
    Custom permission to allow users with any role to access a project.
    """
    def has_object_permission(self, request, view, obj):
        try:
            return obj.projectuser_set.filter(user=request.user).exists()
        except:
            return False 