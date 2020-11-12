import requests
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import *
from realtime.messaging import send_event_request, send_event_response_request, send_firebase_push
from .models import *
from .serializers import EventSerializer, RequestSerializer, ExtendedEventSerializer


class EventListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = ExtendedEventSerializer
    queryset = Event.objects.all()
    offset = 15

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(creator=self.request.user, categories=request.data.get('categories'))
            event.members.add(request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q()

        user_id = request.GET.get('user_id')
        if user_id is not None and user_id != '':
            if UserProfile.objects.filter(id=user_id):
                user = UserProfile.objects.filter(id=user_id)[0]
            else:
                user = self.request.user
        else:
            user = self.request.user

        if request.GET.get('text') is not None and request.GET.get('text') != '':
            q = q & filter_by_text(request.GET.get('text'))

        if request.GET.get('me') is not None and request.GET.get('me') != '':
            if request.GET.get('me') == 'part':
                q = q & taking_part(user=user)
            elif request.GET.get('me') == 'not_part':
                q = q & not_taking_part(user=user)

        if request.GET.get('requested') is not None and request.GET.get('requested') != '':
            if request.GET.get('requested') == 'not_answered':
                q = q | not_answered_requests(user=user)
            elif request.GET.get('requested') == 'not_requested':
                q = q & not_requested_events(user=user)

        if request.GET.get('ended') is not None and request.GET.get('ended') != '':
            if request.GET.get('ended') == 'true':
                q = q & ended_events()
            elif request.GET.get('ended') == 'false':
                q = q & ~ended_events()

        q = q & filter_by_categories(request.GET.getlist('category'))
        q = q & filter_by_text(request.GET.get('text'))
        q = q & filter_by_age(request.GET.get('from_age'), request.GET.get('to_age'))
        q = q & filter_by_sex(request.GET.getlist('sex'))
        q = q & filter_by_geo(request.GET.get('latitude'), request.GET.get('longitude'), request.GET.get('distance'))

        events = self.queryset.filter(q).distinct().order_by('-id')

        if request.GET.get('offset') is not None and request.GET.get('offset') != '':
            last_event_id = request.GET.get('offset')
            events = events[int(last_event_id): int(last_event_id) + self.offset]

        for event in events:
            try:
                event.requested = True if Request.objects.get(from_user=user, event=event,
                                                              decision=Decision.NO_ANSWER.value) else False
            except Request.DoesNotExist:
                event.requested = False

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
            serializer.save(categories=request.data.get('categories'))
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

            send_firebase_push(
                title='Новая заявка!',
                message=request.user.first_name + ' ' + request.user.last_name + ' хочет вступить в ваше событие',
                content_type='REQUEST',
                content_id=event.id,
                to_user_token=UserProfile.objects.get(pk=to_user.id).firebase_uid
            )

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

    @staticmethod
    def send_message(event_id, user):
        text = user.first_name + ' вступил в событие!'
        data = {'event': event_id, 'text': text, 'is_systemic': 'true'}
        token = Token.objects.get(user=user)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Token ' + token.key}
        requests.post('https://meetingappbackend.xyz:443/api/messages/', data=data, headers=headers)

    def put(self, request, pk):
        event_request = self.get_object(pk)

        serializer = RequestSerializer(event_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(seen=True)

            decision = ' отклонил Вашу заявку :('
            event = Event.objects.get(id=serializer.data.get('event'))
            user = UserProfile.objects.get(id=serializer.data.get('from_user').get('id'))

            if serializer.data.get('decision') == Decision.ACCEPT.value:
                event.members.add(user)
                decision = ' одобрил Вашу заявку :)'
                self.send_message(event.id, user)

            self.send_websocket(serializer.data.get('id'))

            send_firebase_push(
                title='Ваша заявка была рассмотрена!',
                message=request.user.first_name + ' ' + request.user.last_name + decision,
                content_type='REQUEST',
                content_id=event.id,
                to_user_token=UserProfile.objects.get(pk=user.id).firebase_uid
            )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        Request.objects.filter(pk=pk).delete()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
