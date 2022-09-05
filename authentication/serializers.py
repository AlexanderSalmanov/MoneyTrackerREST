from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.contrib.auth import authenticate

from .models import User



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=64, min_length=4)
    password = serializers.CharField(max_length=64, min_length=4, write_only=True)
    tokens = serializers.SerializerMethodField()


    def get_tokens(self, obj):

        user = User.objects.get(email=obj.get('email'))

        return {
            'access': user.tokens().get('access'),
            'refresh': user.tokens().get('refresh')
        }


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            email=email,
            password=password
        )
        if not user:
            raise AuthenticationFailed("This user doesn't exist.")
        if not user.is_active:
            raise AuthenticationFailed("This account is inactive.")
        if not user.is_verified:
            raise AuthenticationFailed("This account is not verified.")

        user_obj = User.objects.get(email=email)

        return {
            'email': attrs.get('email'),
            'tokens': user_obj.tokens()
        }

class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=4)


    def validate(self, attrs):
        email = attrs.get('email')

        return super().validate(attrs)

class PasswordResetSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=128, min_length=4, write_only=True)
    token = serializers.CharField(max_length=555, write_only=True)
    uidb64 = serializers.CharField(max_length=64, write_only=True)


    def validate(self, attrs):

        try:

            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))

            user_obj = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user_obj, token):
                raise AuthenticationFailed('This password reset token has already been used.', 401)

            user_obj.set_password(password)
            user_obj.save()
            return user

        except Exception as e:
            return AuthenticationFailed('This password reset token is invalid, try getting another one.', 401)
