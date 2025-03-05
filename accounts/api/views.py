from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication

from accounts.models import User
from accounts.api.permissions import IsOwner
from accounts.api.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsOwner]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
