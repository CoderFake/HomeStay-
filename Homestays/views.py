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
from .models import Homestays, HomestayImages, Facilities
from .serializers import HomestaySerializer
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from botocore.exceptions import NoCredentialsError
import boto3
from django.utils import timezone

User = get_user_model()


class HomestaysView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'adminapp/homestays/homestay_list.html'

    def get(self, request):
        return Response(template_name=self.template_name)

