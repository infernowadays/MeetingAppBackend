from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realtime.messaging import send_message
from .serializers import *


class ChatView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        chat = self.get_object(pk)
        serializer = ChatSerializer(chat)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def send_websocket(pk, chat_members):
        send_message(
            message=Message.objects.get(pk=pk),
            chat_members=chat_members
        )

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            message = serializer.data
            chat_members = Chat.objects.get(id=message.get('chat').id).members

            self.send_websocket(message.get('id'), chat_members)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
