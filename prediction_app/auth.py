from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.conf import settings
import jwt
from django.http import JsonResponse

from .serializer import UserSerializer
from .user_utils import get_user_data

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginAPIView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_toke = str(refresh)
            decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            # print(decoded_token)
            user_id= decoded_token.get('user_id')
            user_data = get_user_data(user_id)
            # print(user_data)
            response = JsonResponse({'message': 'Success'})
            response['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Replace with your frontend domain
            response['Access-Control-Allow-Credentials'] = 'true'
            return Response(
                user_data, response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class IsAuthenticatedAPIView(APIView):
    def get(self, request):
        session_id = request.COOKIES.get('sessionid')

        if session_id is not None:
            try:
                session = Session.objects.get(session_key=session_id)
                user_id = session.get_decoded().get('_auth_user_id')
                user = User.objects.get(id=user_id)
                # print(user)
                user_data = {
                    'user_id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'last_searched_stock': user.last_searched_stock,
                }

                return Response(user_data, status=status.HTTP_200_OK)
            except (Session.DoesNotExist, User.DoesNotExist):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
