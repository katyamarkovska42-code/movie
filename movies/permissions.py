from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    message = "Ви можете змінювати лише власні фільми."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or obj.owner_id == request.user.id
            )
        )
