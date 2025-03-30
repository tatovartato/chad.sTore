from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny 
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from products.permissions import IsObjectOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class UserViewSet(mixins.ListModelMixin, 
                  mixins.RetrieveModelMixin, 
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProfilViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]

    def get_object(self):
        return self.request.user
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
     
    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
class PasswordResetRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            #Token Gneration
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            #Password reset URL generation
            reset_url = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64":uid, "token":token})
            )

            #Send email
            send_mail(
                "password recovery",
                f"click the url to reset your password: {reset_url}",
                "noreply@example.com",
                [user.email],
                fail_silently=False
            )

            return Response(
                {"message":"link sent to email"}, status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmSerializerViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetConfirmSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, description="User ID (base64 encoded)", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING),
        ]
    )
    
    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message":"Password successfully updated"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)