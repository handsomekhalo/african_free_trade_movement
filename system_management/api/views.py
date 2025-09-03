import datetime
from datetime import datetime
import json
import random
from requests import Response
from system_management import constants
# from system_management.api.serializers import DeleteUserSerializer, GetAlltUserModelSerializer, RegisterSerializer, UserModelSerializer, UserTypeModelSerializer, UserUpdateSerializer,CreateUserSerializer
from system_management.api.serializers import RegisterSerializer, UserModelSerializer
from system_management.models import User, UserType
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status


from rest_framework.decorators import api_view, permission_classes

from rest_framework import (
    status,
    permissions,
    authentication
)

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)



@api_view(["POST"])
@permission_classes((AllowAny,))
def login_api(request):
    """
    Login API for user authentication
    """
    body = json.loads(request.body)
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return Response(
            {"status": "error", "message": "Please provide both email and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(email=email, password=password)

    if not user:
        return Response(
            {"status": "error", "message": "Invalid Credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {"status": "error", "message": "User is inactive, please contact admin"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)

    otp = "".join([str(random.randint(0, 9)) for _ in range(5)])  # temporary if needed

    user.last_login = datetime.now()
    user.save()

    user_serializer = UserModelSerializer(user)

    return Response(
        {
            "status": "success",
            "token": token.key,
            "otp": otp,
            "user": user_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user_api(request):
    """
    Register a new user (Admin / Exporter / Logistics Provider)
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "status": "success",
                "user_id": user.id,
                "email": user.email,
                "user_type": user.user_type.name,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout_api(request):
    """
    Logout API for user authentication.

    Deletes the current user's authentication token if present
    and returns a JSON response indicating success.

    Expected header:
        Authorization: Token <token_value>
    """
    try:
        if request.auth:
            request.auth.delete()
            return Response(
                {"status": "success", "message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )
        else:
            # Token missing or already deleted
            return Response(
                {"status": "success", "message": "Already logged out"},
                status=status.HTTP_200_OK
            )
    except Exception as e:
        return Response(
            {"status": "error", "message": f"Logout failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
