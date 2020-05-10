import firebase_admin
from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from firebase_admin import credentials
from firebase_admin import messaging
from pyfcm import FCMNotification
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realtime.messaging import send_event_request, send_event_response_request
from .enums import Decision
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


# def post(request):
#     serializer = EventSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(creator=request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def not_requested_events(self):
        events_ids = Event.objects.all().values_list('id', flat=True)
        requested_events = Request.objects.filter(event__in=events_ids, from_user=self.request.user).values_list(
            'event', flat=True)

        return ~Q(id__in=requested_events)

    def filter_events_by_user_roles(self, list_roles):
        q = Q()
        if list_roles:
            for role in list_roles:
                if role == 'creator':
                    q = q | Q(creator=self.request.user)
                elif role == 'member':
                    q = q | Q(members=self.request.user)

        else:
            q = Q(~Q(creator=self.request.user) & ~Q(members=self.request.user) & self.not_requested_events())

        return q

    @staticmethod
    def filter_events_by_categories(list_categories):
        if list_categories:
            categories = Category.objects.filter(name__in=list_categories).values_list('id', flat=True)
            return Q(categories__in=categories)
        else:
            return Q()

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q() | self.filter_events_by_user_roles(request.GET.getlist('me'))
        q = q & self.filter_events_by_categories(request.GET.getlist('category'))

        events = Event.objects.filter(q).distinct().order_by('-id')
        serializer = EventSerializer(instance=events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EventDetailView(APIView):
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


class RequestsListView(APIView):
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
            from_user = self.get_object(request.data['from_user'])
            to_user = self.get_object(request.data['to_user'])

            event = Event.objects.get(id=request.data['event'])
            serializer.save(from_user=from_user, to_user=to_user, event=event)

            self.send_websocket(serializer.data.get('id'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        requests = Request.objects.filter(to_user=request.user).order_by('-created')
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

            if serializer.data.get('decision') == Decision.ACCEPT:
                event = Event.objects.get(id=serializer.data.get('event'))
                user = UserProfile.objects.get(email=serializer.data.get('from_user'))
                event.members.add(user)
            elif serializer.data.get('decision') == Decision.DECLINE:
                event_request.delete()

            # self.send_websocket(serializer.data.get('id'))

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
