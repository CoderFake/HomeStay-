from django.db.migrations import serializer
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsRegularUser, IsStaffUser, IsSuperUser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
from Accounts.serializers import (UserLoginSerializer, ResendEmailVerificationSerializer, UserSerializer, UserProfileSerializer, UserPictureDeleteSerializer)
from Homestays.serializers import HomestaySerializer, HomestayUpdateCreateSerializer
from Homestays.models import HomestayImages, Homestays, Facilities, Rooms
from .serializers import AdminLoginSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from botocore.exceptions import NoCredentialsError
import boto3

User = get_user_model()


class DashboardView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'adminapp/index.html'

    def get(self, request):
        return Response(template_name=self.template_name)


class PermissionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStaffUser]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


#===================================================================
#                              user
#===================================================================


class UserAdminView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'adminapp/accounts/user_list.html'

    def get(self, request):
        return Response(template_name=self.template_name)


class UserListView(ListAPIView):

    queryset = User.objects.filter(status="active")
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        print(request.user)
        return self.list(request, *args, **kwargs)


class UserView(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStaffUser]
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)

        if request.user == user:
            pass
        elif not request.user.is_superuser:
            return Response({"message": "You do not have permission to edit other users."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'adminapp/accounts/edit_user.html'

    def get(self, request):
        return Response(template_name=self.template_name)


#==============================================================
#                         Homestays
#==============================================================


class HomestayAdminView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'adminapp/homestays/homestay_list.html'

    def get(self, request):
        return Response(template_name=self.template_name)


class HomestayListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStaffUser]
    queryset = Homestays.objects.filter(is_deleted=False)
    serializer_class = HomestaySerializer


class HomestayCreateUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]
    serializer_class = HomestayUpdateCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not request.user.is_superuser:
            return Response({"message": "You do not have permission to create homestay"}, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Homestay created successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"message": "You do not have permission to edit homestay"}, status=status.HTTP_403_FORBIDDEN)
        homestay_id = self.request.query_params.get('homestay_id')
        homestay = get_object_or_404(Homestays, id=homestay_id)
        serializer = self.serializer_class(homestay, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Edited homestay successfully", status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"message": "You do not have permission to delete homestay"}, status=status.HTTP_403_FORBIDDEN)
        homestay_id = self.request.query_params.get('homestay_id')
        homestay = get_object_or_404(Homestays, id=homestay_id)
        serializer = self.serializer_class()
        serializer.delete_homestay(homestay)
        return Response("Deleted homestay successfully", status=status.HTTP_204_NO_CONTENT)




