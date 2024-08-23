from django.db.migrations import serializer
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsRegularUser, IsStaffUser, IsSuperUser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (UserRegisterSerializer, UserLoginSerializer, ResendEmailVerificationSerializer, ForgotPasswordSerializer,
                          ResetPasswordConfirmSerializer, UserProfileSerializer, UserPictureDeleteSerializer)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from botocore.exceptions import NoCredentialsError
import boto3
from django.utils import timezone

User = get_user_model()


class CustomRefreshToken(RefreshToken):
    @classmethod
    def get_token(cls, user):
        token = super().for_user(user)
        token['email'] = user.email
        return token


def send_verification_email(request, user):
    refresh = CustomRefreshToken.get_token(user)
    current_site = get_current_site(request)
    verify_url = "accounts/verify_email"

    mail_subject = "Activate your account"
    parameters = {
        'full_name': f'{user.first_name} {user.last_name}',
        'verification_link': f"http://{current_site}/{verify_url}?token={str(refresh.access_token)}"
    }
    mail_body = render_to_string('accounts/verify.html', parameters)
    mail = EmailMessage(
        subject=mail_subject,
        body=mail_body,
        from_email=config('EMAIL_HOST_USER'),
        to=[user.email]
    )
    mail.content_subtype = "html"
    try:
        user.reset_password_token = str(refresh.access_token)
        user.save()
        mail.send()
    except Exception as e:
        raise ValueError(f"Error sending email: {e}")


class VerifyTokenEmail(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        token =request.query_params.get('token')
        if token is None:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id, status="inactive")
            if user.reset_password_token != str(token):
                return Response({"error": "No token provided"}, status=status.HTTP_404_NOT_FOUND)
            if user.status == "inactive":
                user.status = "active"
                user.reset_password_token = None
                user.save()
                return Response({"success": "User has been activated"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "User is already activated"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"error": "Token is invalid or expired", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendEmailView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            send_verification_email(self.request, user)
            return Response("Email sent successfully", status=status.HTTP_200_OK)


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(self.request, user)
        return Response(status=status.HTTP_201_CREATED)


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email, status="active")
            except User.DoesNotExist:
                return Response("User does not exist", status=status.HTTP_404_NOT_FOUND)

            refresh = CustomRefreshToken.get_token(user)
            reset_password_token = str(refresh.access_token)
            current_site = get_current_site(self.request)
            reset = "accounts/confirm_reset_password"

            mail_subject = "Reset Your Password"
            parameters = {
                'full_name': f'{user.first_name} {user.last_name}',
                'reset_pass_link': f"http://{current_site}/{reset}?token={reset_password_token}"
            }
            mail_body = render_to_string('accounts/reset_password_email.html', parameters)
            mail = EmailMessage(
                subject=mail_subject,
                body=mail_body,
                from_email=config('EMAIL_HOST_USER'),
                to=[user.email]
            )
            mail.content_subtype = "html"
            try:
                mail.send()
                user.reset_password_token = reset_password_token
                user.save()
            except Exception as e:
                raise ValueError(f"Error sending email: {e}")
            return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ConfirmResetPassword(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            token = request.query_params.get('token')
            if token is None:
                return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reset_password_token = AccessToken(token)
                user_id = reset_password_token['user_id']
                user = User.objects.get(id=user_id)
                if user.reset_password_token != str(token):
                    return Response("Invalid token", status=status.HTTP_404_NOT_FOUND)
                user.reset_password_token = None
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"success": "Password has been changed"}, status=status.HTTP_200_OK)

            except TokenError as e:
                return Response({"error": "Token is invalid or expired", "details": str(e)},
                                status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        print(serializer.errors)
        return Response("error", status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'accounts/register.html'

    def get(self, request):
        return Response(template_name=self.template_name)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            user.last_login = timezone.now()
            user.save()
            refresh = RefreshToken.for_user(user)

            response = Response({
                'detail': 'Login successful',
                'access_token': str(refresh.access_token),
                'user_id': user.id,
            }, status=status.HTTP_200_OK)

            return response
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    def post(self, request):
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        return response


class UserProfileUpdateView(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsRegularUser]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class DeleteUserPictureView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsRegularUser]

    def delete(self, request, *args, **kwargs):
        serializer = UserPictureDeleteSerializer(instance=request.user, context={'view': self})
        user = serializer.save()
        return Response({'status': 'picture deleted'}, status=200)

    def delete_from_s3(self, key):
        s3_client = boto3.client('s3')
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
