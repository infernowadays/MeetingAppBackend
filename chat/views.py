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

    def init_chat(self, event, last_message):
        chat = dict({})
        chat['content_type'] = 'message'
        chat['content_id'] = event.id
        chat['title'] = event.description
        chat['from_user'] = event.creator

        if last_message == '':
            chat['last_message'] = ''
            chat['last_message_id'] = 0
            chat['last_seen_message_id'] = 0
            chat['last_message_created'] = str(event.created).replace(' ', 'T').replace('+00:00', 'Z')
            chat['last_message_from_user_name'] = ''

        else:
            chat['last_message'] = last_message.text
            chat['last_message_id'] = last_message.id
            try:
                chat['last_seen_message_id'] = \
                    self.request.user.last_messages.filter(chat_id=event.id).order_by('-message_id')[0].message_id
            except IndexError:
                chat['last_seen_message_id'] = 0
            chat['last_message_created'] = str(last_message.created).replace(' ', 'T').replace('+00:00', 'Z')
            chat['last_message_from_user_name'] = last_message.from_user.first_name

        return chat

    @staticmethod
    def get_last_message(event_id):
        try:
            last_message = Message.objects.filter(event_id=event_id).order_by("-id")[0]
        except IndexError:
            last_message = ''

        return last_message

    def get(self, request):
        if request.GET.get('chat_id') is not None and request.GET.get('chat_id') != '':
            event = Event.objects.get(id=request.GET.get('chat_id'))
            last_message = self.get_last_message(event.id)
            serializer = ChatSerializer(instance=[self.init_chat(event, last_message)], many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        members_events = request.user.members_events.all()
        creator_events = request.user.creator_events.all()
        events = set(members_events | creator_events)

        chats = list([])
        # messages from events
        for event in events:
            last_message = self.get_last_message(event.id)
            chats.append(self.init_chat(event, last_message))

        serializer = ChatSerializer(instance=chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    offset = 50

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

    def see_previous_messages(self, data):
        serializer = LastSeenMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(from_user=self.request.user)

            event = Event.objects.get(id=request.data['event'])
            members_ids = event.members \
                .all() \
                .filter(~Q(id=request.user.id)) \
                .values_list('id', flat=True)

            self.send_websocket(serializer.data.get('id'), members_ids)
            for member_id in members_ids:
                send_firebase_push(
                    title=request.user.first_name + ' ' + request.user.last_name,
                    message=request.data.get('text'),
                    content_type='MESSAGE',
                    content_id=request.data.get('event'),
                    to_user_token=UserProfile.objects.get(pk=member_id).firebase_uid
                )

            self.see_previous_messages({'chat_id': event.id, 'message_id': serializer.data.get('id')})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, event_id):
        event = self.get_object(event_id)

        messages = event.messages.all().order_by('created')

        if request.GET.get('offset') is not None and request.GET.get('offset') != '':
            first_message_id = int(request.GET.get('offset'))

            left = len(messages) - first_message_id - self.offset
            left = 0 if left < 0 else left

            right = len(messages) - first_message_id
            right = 0 if right < 0 else right

            messages = messages[left: right]

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
            members_ids.append(user.id)

            self.send_websocket(serializer.data.get('id'), members_ids)

            send_firebase_push(request.user.first_name + ' ' + request.user.last_name, request.data.text,
                               'private_message', request.data.ticket.id,
                               UserProfile.objects.get(pk=user.id).firebase_uid)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        user = self.get_object(user_id)

        q = Q(Q(from_user=request.user) & Q(user=user)) | Q(Q(from_user=user) & Q(user=request.user))

        messages = PrivateMessage.objects.filter(q).order_by('created')
        serializer = PrivateMessageSerializer(instance=messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LastSeenMessageListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = LastSeenMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
