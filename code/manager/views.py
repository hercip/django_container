from rest_framework import viewsets, status, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from manager.models import AppUser, MenuItem
from .serializers import MenuItemSerializer, AppUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# class UserProfileView(MultiSerializerModelViewSet):
#     queryset = UserProfile.objects.all()
#     base_nested_fields = ['user']
#     base_serializer = UserProfileBaseSerializer

#     action_serializers = {
#         'list':             UserProfileSerializer,              # get
#         'retrieve':         UserProfileSerializer,              # get details
#         'create':           UserProfileSerializer,              # post
#         'update':           UserProfileSerializer,              # put
#         'partial_update':   UserProfileSerializer,              # patch
#     }

class AppUserView(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

# class AppUserView(MultiSerializerModelViewSet):
#     queryset = AppUser.objects.all()
#     # base_nested_fields = ['user']
#     # base_serializer = UserProfileBaseSerializer

#     # reset password - extra action
#     # https://www.django-rest-framework.org/api-guide/routers/#routing-for-extra-actions

#     action_serializers = {
#         'list':             AppUserSerializer,              # get
#         'retrieve':         AppUserSerializer,              # get details
#         'create':           AppUserSerializer,              # post
#         'update':           AppUserSerializer,              # put
#         'partial_update':   AppUserSerializer,              # patch
#     }

class MenuItemView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class RemoveAuthToken(APIView): # logout
    permission_classes = ()

    def delete(self, request):
        if request.auth:
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


remove_auth_token = RemoveAuthToken.as_view()


class ManagerObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_data = AppUserSerializer(user).data
        return Response({'token': token.key, 'user': user_data})

obtain_auth_token = ManagerObtainAuthToken.as_view()


class RegisterUserAPI(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": AppUserSerializer(user, context=self.get_serializer_context()).data,

        })


register_view = RegisterUserAPI.as_view({'get': 'list'})
