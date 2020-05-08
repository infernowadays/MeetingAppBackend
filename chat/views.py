from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realtime.messaging import send_message, send_private_message
from .models import *
from .serializers import *


class MessageView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    @staticmethod
    def send_websocket(pk, members_ids):
        send_message(
            message=Message.objects.get(pk=pk),
            members_ids=members_ids
        )

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            event = Event.objects.get(id=request.data['event'])
            serializer.save(from_user=request.user, event=event)

            members_ids = event.members\
                .all()\
                .filter(~Q(id=request.user.id))\
                .values_list('id', flat=True)

            self.send_websocket(serializer.data.get('id'), members_ids)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, event_id):
        event = self.get_object(event_id)
        messages = event.messages.all()
        serializer = MessageSerializer(instance=messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivateMessageView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    @staticmethod
    def send_websocket(pk, members_ids):
        send_private_message(
            message=PrivateMessage.objects.get(pk=pk),
            members_ids=members_ids
        )

    def post(self, request):
        serializer = PrivateMessageSerializer(data=request.data)
        if serializer.is_valid():
            user = UserProfile.objects.get(id=request.data.get('user'))
            serializer.save(from_user=request.user, user=user)

            members_ids = list([])
            members_ids.append(request.user.id)
            members_ids.append(user.id)

            self.send_websocket(serializer.data.get('id'), members_ids)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        user = self.get_object(user_id)

        q = Q(Q(from_user=request.user) & Q(user=user)) | Q(Q(from_user=user) & Q(user=request.user))

        messages = PrivateMessage.objects.filter(q)
        serializer = PrivateMessageSerializer(instance=messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
