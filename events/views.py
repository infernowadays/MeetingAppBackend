from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import *
from realtime.messaging import send_event_request, send_event_response_request, send_firebase_push
from .models import *
from .serializers import EventSerializer, RequestSerializer


class EventListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(creator=self.request.user, categories=request.data.get('categories'))
            event.members.add(request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q()
        if request.GET.getlist('me') is not None and request.GET.getlist('me') != []:
            q = q & filter_by_user_roles(list_roles=request.GET.getlist('me'), user=request.user)

        if request.GET.get('requested') is not None and request.GET.get('requested') != '':
            if request.GET.get('requested') == 'true':
                q = q | requested_events(user=request.user)
            elif request.GET.get('requested') == 'false':
                q = q | ~requested_events(user=request.user)

        if request.GET.get('ended') is not None and request.GET.get('ended') != '':
            if request.GET.get('ended') == 'true':
                q = q & ended_events(queryset=self.queryset, user=request.user)
            elif request.GET.get('ended') == 'false':
                q = q & not_ended_events(queryset=self.queryset, user=request.user)

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

    def put(self, request, pk):
        event_request = self.get_object(pk)
        Request.objects.filter(pk=pk).update(seen=True)

        serializer = RequestSerializer(event_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            decision = ' отклонил Вашу заявку :('
            event = Event.objects.get(id=serializer.data.get('event'))
            user = UserProfile.objects.get(id=serializer.data.get('from_user').get('id'))

            if serializer.data.get('decision') == Decision.ACCEPT.value:
                event.members.add(user)
                decision = ' одобрил Вашу заявку :)'

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
