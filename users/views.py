from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny 
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, EmailResendCodeSerializer, EmailCodeConfirmSerializer
from products.permissions import IsObjectOwnerOrReadOnly
from users.models import EmailVerificationCode
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta
import random   

User = get_user_model()

class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            self.send_verification_code(user)
            return Response(
                {"detail":"User registered successfully. Verification code sent to email"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_code(self, user):
        code = str(random.randint(100000, 999999))
        
        EmailVerificationCode.objects.update_or_create(
            user=user,
            defaults={'code':code, 'created_at':timezone.now()}
        )
        subject ="Your verification code"
        message = f"Hello {user.username},\nYour verification code is: {code}"

        send_mail(subject, message, 'no_replay@example.com', [user.email] )
    
    @action(detail=False, methods=["post"], url_path="resend_code", serializer_class=EmailResendCodeSerializer)
    def resend_code(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        user = serializer.validated_data["user"]
        existing = EmailVerificationCode.objects.filter(user=user).first()
        if existing:
            time_diff = timezone.now() - existing.created_at
            if time_diff < timedelta(minutes=1):
                wait_seconds = 60 - int(time_diff.total_seconds())
                return Response(
                    {"detail":f"Please wait {wait_seconds} seconds before requesting a new code"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        self.send_verification_code(user)
        return Response({"detail": "Verification code recent successfully"})
    
    @action(detail=False, methods=['post'], url_path='confirm_code', serializer_class=EmailCodeConfirmSerializer)
    def confirm_code(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return Response({"message": "user is successfully activated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64":uid, "token":token})
            )

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