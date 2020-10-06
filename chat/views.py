from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realtime.messaging import send_message, send_private_message, send_firebase_push
from .models import *
from .serializers import *


class ChatsView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        members_events = request.user.members_events.all()
        creator_events = request.user.creator_events.all()
        events = set(members_events | creator_events)

        serializer = EventSerializer(instance=events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            serializer.save(from_user=request.user)

            event = Event.objects.get(id=request.data['event'])
            members_ids = event.members \
                .all() \
                .filter(~Q(id=request.user.id)) \
                .values_list('id', flat=True)

            # members_ids.

            self.send_websocket(serializer.data.get('id'), members_ids)
            for member_id in members_ids:
                send_firebase_push(request.user.first_name + ' ' + request.user.last_name, request.data, UserProfile.objects.get(pk=member_id).firebase_uid)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, event_id):
        event = self.get_object(event_id)
        messages = event.messages.all().order_by('created')
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
