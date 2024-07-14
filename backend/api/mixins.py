from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


class DjoserPermissionsMethodsMixin:
    """Переопределяет разрешения и методы класса UserViewSet Djoser."""

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = (AllowAny,)
        elif self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            data={"detail": 'Метод "PUT" не разрешен.'},
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            data={"detail": 'Метод "PATCH" не разрешен.'},
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            data={"detail": 'Метод "DELETE" не разрешен.'},
        )

    def activation(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def resend_activation(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def reset_password(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def reset_password_confirm(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def set_username(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def reset_username(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    def reset_username_confirm(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )
