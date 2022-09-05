from django.shortcuts import render
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignupSerializer, EmailVerificationSerializer, LoginSerializer,
    RequestPasswordResetEmailSerializer, PasswordResetSerializer
)
from .models import User
from .utils import Util

import jwt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# Create your views here.

class SignupAPIView(generics.GenericAPIView):
    """
    Signup portion. User is prompted to enter his/her email, full name and password,
    then the server responds with an email which contains account verification link.
    """

    serializer_class = SignupSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            user_data = serializer.data
            user_obj = User.objects.get(email=user_data.get('email'))
            # This section is implemented only for allowing newly created users
            # be redirected to the page where they can verify their account.
            # Thats why only the access token gets fetched.
            token = RefreshToken.for_user(user_obj).access_token

            current_site = get_current_site(request).domain
            relative_link = reverse('authentication:verify-email')
            absurl = f"http://{current_site}{relative_link}?token={token}"
            email_body = f"Greetings, {user_obj.full_name}!\nUse the link below to verify your email:\n{absurl}"

            data = {
                'to': user_obj.email,
                'subject': 'Verify your email',
                'body': email_body
            }

            Util.send_email(data)

            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailAPIView(generics.GenericAPIView):
    """
    Directly in the API, this endpoint fetches the token related to an email,
    and, in case an account associated to it is verified, the application issues a simple success response.
    Generally, this endpoint receives an email, the token associated to an account with a given email,
    and then verifies (sets `is_verified` attribute to `True`) an account.
    """

    serializer_class = EmailVerificationSerializer
    pagination_class = None

    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY,
        description='Provide your access token',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user_obj = User.objects.get(id=payload.get('user_id'))
            if not user_obj.is_verified:
                user_obj.is_verified = True
                user_obj.save()
                return Response({
                    'Success': 'Your account has been verified!'
                }, status=status.HTTP_200_OK)

        except jwt.DecodeError as e:
            return Response({
                'Error': 'Your token is invalid, consider receiving a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError as e:
            return Response({
                'Error': 'Activation link has expired. Consider receiving a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    """
    Basic authentication portion additionally returning user's Access and Refresh
    JWT tokens for further interaction with an API.
    """

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    """
    Takes in an email address, and then issues an email message containing a link with a Password Reset token.
    """

    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):

        email = request.data.get('email')

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            user_obj = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(
                str(user_obj.id).encode('utf-8')
            )

            token = PasswordResetTokenGenerator().make_token(user_obj)

            current_site = get_current_site(request).domain
            relative_link = reverse('authentication:password-reset-confirm', kwargs={
                'uidb64': uidb64,
                'token': token
            })
            absurl = f"http://{current_site}{relative_link}"

            email_body = f"Hi there!\nUse the link below to reset your password:\n{absurl}"

            data = {
                'to': user_obj.email,
                'body': email_body,
                'subject': 'Reset your password'
            }

            Util.send_email(data)

            return Response({
                'Success': True,
                'Message': 'Password reset requested successfully!'
            }, status=status.HTTP_200_OK)

        return Response({
            'Uh Oh': 'Something went wrong!'
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetTokenCheckAPIView(APIView):
    """
    Takes in user's encoded ID and user's Password Reset token and validates it.
    """

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user_obj = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user_obj, token):
                return Response({
                    'Error': 'Token has already been used, request a new one, please.'
                }, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                'Success': True,
                'Message': 'Your credentials are valid!',
                'uidb64': uidb64,
                'token': token
            }, status=status.HTTP_200_OK)


        except DjangoUnicodeDecodeError as e:
            return Response({
                'Error': 'This token is invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)

class PasswordReset(generics.GenericAPIView):
    """
    Takes in user's Password Reset token, user's encoded id (uidb64), and prompts the user to set a new password
    if both of the above credentials are valid.
    """

    serializer_class = PasswordResetSerializer

    def patch(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response({
                'Success': True,
                'Message': 'Password reset succeeded!'
            }, status=status.HTTP_200_OK)
