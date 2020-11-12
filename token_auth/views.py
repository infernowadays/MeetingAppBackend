from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Message
from events.enums import Decision
from events.models import Request
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
        serializer = AuthCredentialsSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = validated_data['email']
        password = validated_data['password']

        user = authenticate(email=email, password=password)
        if not user:
            raise Http404
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})


class UploadPhotoView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = ProfilePhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save()

            profile = request.user
            profile.photo = photo
            profile.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        user = self.get_object(pk=pk)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user = request.user
        try:
            current_password = request.data['current_password']
            new_password = request.data['new_password']
        except KeyError:
            raise Http404

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
        else:
            raise Http404

        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})

    def get(self, request):
        serializer = UserProfileSerializer(self.request.user)
        serializer_data = serializer.data

        # new requests count
        q_accepted_and_declined = Q() | Q(decision=Decision.ACCEPT.value) | Q(decision=Decision.DECLINE.value)
        q_accepted_and_declined_for_sender = q_accepted_and_declined & Q(from_user=self.request.user)
        q_not_answered_for_receiver = Q() | Q(decision=Decision.NO_ANSWER.value) & Q(to_user=self.request.user)
        q_not_seen_requests_for_user = (q_accepted_and_declined_for_sender | q_not_answered_for_receiver)

        new_requests_count = Request.objects.filter(q_not_seen_requests_for_user).count()
        serializer_data['new_requests_count'] = new_requests_count

        # new messages count
        new_messages_count = 0
        for last_message in self.request.user.last_messages.all():
            if last_message.message_id - Message.objects.filter(event_id=last_message.chat_id).order_by('-id')[0].id != 0:
                new_messages_count += 1

        serializer_data['new_messages_count'] = new_messages_count

        return Response(serializer_data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(categories=request.data.get('categories'))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        self.request.user.set_password(request.data.get('password'))
        self.request.user.save()

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class FirebaseTokenView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def put(self, request):
        UserProfile.objects.filter(pk=request.user.pk).update(firebase_uid=request.data)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
