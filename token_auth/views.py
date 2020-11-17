from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Message, LastSeenMessage
from email_service.models import ConfirmationCode
from events.enums import Decision
from events.models import Event
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


class ForgetPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForgetPasswordSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        email = validated_data['email']
        code = validated_data['code']

        confirmation = ConfirmationCode.objects.filter(email=email).order_by('-id')[0]
        if not confirmation or not UserProfile.objects.filter(email=email):
            raise Http404

        if code == str(confirmation.code):
            user = UserProfile.objects.get(email=email)
            user.set_password(validated_data['new_password'])
            user.save()
            Token.objects.get_or_create(user=user)
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'wrong code'}, status=status.HTTP_404_NOT_FOUND)


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

        q_accepted_and_declined = Q() | Q(decision=Decision.ACCEPT.value) | Q(decision=Decision.DECLINE.value)
        q_accepted_and_declined_for_sender = q_accepted_and_declined & Q(from_user=self.request.user) & Q(seen=False)
        q_not_answered_for_receiver = Q() | Q(decision=Decision.NO_ANSWER.value) & Q(to_user=self.request.user)
        q_not_seen_requests_for_user = (q_accepted_and_declined_for_sender | q_not_answered_for_receiver)
        requests = Request.objects.filter(q_not_seen_requests_for_user).values('id', 'from_user', 'to_user', 'decision',
                                                                               'seen')
        serializer_data['requests'] = requests

        chats = list([])
        events = Event.objects.filter(Q(creator=self.request.user) | Q(members=self.request.user))
        for event in events:
            chat = dict({})
            chat['content_id'] = event.id
            event_messages = Message.objects.filter(event=event).order_by('-id')

            try:
                chat['last_seen_message_id'] = LastSeenMessage.objects.get(chat_id=event.id,
                                                                           user=self.request.user).message_id
            except LastSeenMessage.DoesNotExist:
                chat['last_seen_message_id'] = 0

            if len(event_messages) > 0:
                chat['last_message_id'] = event_messages[0].id

                if event_messages[0].id > chat.get('last_seen_message_id'):
                    chats.append(chat)

        serializer_data['chats'] = chats

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
