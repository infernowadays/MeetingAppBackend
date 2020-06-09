from django.http import Http404
from django.http import JsonResponse
from firebase_admin import messaging
from pyfcm import FCMNotification
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import *
from realtime.messaging import send_event_request, send_event_response_request
from token_auth.serializers import UserProfileSerializer
from .models import *
from .serializers import EventSerializer, RequestSerializer


class PushView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        # init_app()
        api_key = ''
        push_service = FCMNotification(api_key=api_key)

        # OR initialize with proxies

        proxy_dict = {
            "http": "http://127.0.0.1",
            "https": "http://127.0.0.1",
        }
        push_service = FCMNotification(api_key=api_key, proxy_dict=proxy_dict)

        token = ''
        registration_id = token
        message_title = "Uber update"
        message_body = "Hi john, your customized news for today is ready"
        # response = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
        #                                              message_body=message_body)

        # [START send_to_topic]
        # The topic name can be optionally prefixed with "/topics/".
        topic = 'general'
        # See documentation on defining a message payload.

        # message = messaging.Message(
        #     data={
        #         'title': '1234',
        #         'body': 'test',
        #     },
        #     token=token,
        # )

        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title='title',
                    body='body',
                ),
            ),
            token=token,
        )

        # response = push_service.notify_topic_subscribers(topic_name='general', message_body='qq gggggg')

        # Send a message to the devices subscribed to the provided topic.
        response = messaging.send(message)
        return JsonResponse({'response': response}, status=200, safe=False)

        # Response is a message ID string.
        # print('Successfully sent message:', response)
        # [END send_to_topic]


class EventListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            categories = request.data.get('categories')
            if categories is not None:
                event = serializer.save(creator=self.request.user, categories=categories)
            else:
                event = serializer.save(creator=self.request.user)

            event.members.add(request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q() | filter_by_user_roles(list_roles=request.GET.getlist('me'), user=request.user)
        q = q & not_requested_events(queryset=self.queryset, user=request.user)
        q = q & filter_by_categories(request.GET.getlist('category'))

        events = self.queryset.filter(q).distinct().order_by('-id')
        serializer = self.serializer_class(instance=events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EventDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        event = self.get_object(pk)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        event = self.get_object(pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = self.get_object(pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def send_websocket(pk):
        send_event_request(
            event_request=Request.objects.get(pk=pk)
        )

    @staticmethod
    def get_object(pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            to_user = self.get_object(request.data['to_user'])

            event = Event.objects.get(id=request.data['event'])
            serializer.save(from_user=request.user, to_user=to_user, event=event)

            self.send_websocket(serializer.data.get('id'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        requests = Request.objects.filter(Q(to_user=request.user) | Q(from_user=request.user)).order_by('-created')
        serializer = RequestSerializer(instance=requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RespondRequestView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def send_websocket(pk):
        send_event_response_request(
            event_request=Request.objects.get(pk=pk)
        )

    @staticmethod
    def get_object(pk):
        try:
            return Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        event_request = self.get_object(pk)
        serializer = RequestSerializer(event_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            if serializer.data.get('decision') == Decision.ACCEPT.value:
                event = Event.objects.get(id=serializer.data.get('event'))
                user = UserProfile.objects.get(id=serializer.data.get('from_user').get('id'))
                event.members.add(user)
            # elif serializer.data.get('decision') == Decision.DECLINE.value:
            #     event_request.delete()

            self.send_websocket(serializer.data.get('id'))

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
