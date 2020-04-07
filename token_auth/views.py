from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            username = self.request.data['username']
            password = self.request.data['password']
        except KeyError:
            raise Http404

        user = authenticate(username=username, password=password)
        if not user:
            raise Http404
        token = Token.objects.get(user=user)

        return Response({'token': token.key})


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        user = self.get_object(pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirebaseTokenView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def put(self, request):
        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        Token.objects.filter(key=key).update(key=request.data["key"])
        try:
            token = Token.objects.get(key=request.data["key"])
        except Token.DoesNotExist:
            raise Http404

        return Response({"key": token.key}, status=status.HTTP_200_OK)
