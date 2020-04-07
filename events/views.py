import firebase_admin
from django.http import Http404
from django.http import JsonResponse
from firebase_admin import messaging, credentials
from pyfcm import FCMNotification
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EventSerializer, RequestSerializer
from .models import *

from realtime.messaging import send_event_request


def init_app():
    cred = credentials.Certificate(
        {
            "type": "service_account",
            "project_id": "meetingapp-27f7e",
            "private_key_id": "0436b77e71749af3c2d3fb055a125982c6321277",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDL08aBupOJ6jBT\nD6eFT04psDjgMnjr8ckJ9JBrKwJDIdELhMnmui6Qo/d42VQvPgtiFXH0H30ow6Gp\nO5jWZ/R41uATABIwOsPsEYYIFXkXINwuLsvGPT2ehN5Mo7T/4dgUf5qQ4ER9evO5\n9ppE5zoG74zVje/Z1MfiCyRxGPYEbvTdBlGScswdoL5Gvat584UFRzvqJ01ABaFe\neqjj+mCT5YEZO0ZyVSoGRiUVsTChuY+L8ESXA46Riu1SZQjqT7LPY0thVMOKmb3E\nDrglgiYUqP3IIQSzitu1ew3UMbeBBxpX3hcKY8FYjjUKGb+b7N9wy4aCz/xdoleG\niGj1ZTi3AgMBAAECggEADHAdfbuEI7cl88U3+vgrIOG41si9sEg025kQJwbQDVPg\njP9knEiVBtm6ndlFPD/6mdjZ91FK/4dqM6JU+6095RHXr2q8F81X0oc1n2pDO8us\nvY5SSQQu4NMWBz85XSDLx5Rx1JCa6iO5AIp+QRSLHSYJEtvY3Kx4KUcP/KBogtfW\nkeKwcY5lKIk3SdUVBB+Md5PD6O9wyRcqui+QduEywT3EP62w1iEb6CJb4V8nXXJf\ni8okkosT5u3GIXnhFatXyitJ6R4zVMX//N3N0gf+ghJqpaThjQTfIzWOW9zfWIIH\ne5D26x39dopqdo0NrR4ArFGCITjQWp2cW3a9TXx+IQKBgQDzeZG3vUsTE8hbxtU1\ny3Ei5Ld0fqQTrB/nC62/IHRuYb/k+w+n5ALsqIaPqCgv/8BJvDGzTRPDhB4BkNuN\n+97izfiSZUmsyXpnReGIy9Ftq0F4yoNDvQG3Y55968CeXC5pj74wROzYQ0Bb1wVI\n60AcsHJJjvUegkSDoy9aXqa8MwKBgQDWUBGQmV1e+hL7A3GFU3j5WxR/X59Hx7ml\nwLReDzU8jPXjkOkqrb4CZRR9Rh0oYnbT72L6/nml80COZYL3WZipwdJQ2Rxeg6/1\nRBeBMeLfMwLYaIWvbg8ZDGBG5M3JyDi12hIe12GR47BqRHidxzpYSlKuGyZNBQc+\n5mA6g0WNbQKBgFVCzzqOuUmW9eTdvjA2bAoSGgRbjM2uywU328JAdUVqSa7AFH1w\npW2GnoiUFG6qmwW3N5hYd4FSNMfLmHciKq01/8QUYDZ337tmh1JGPbKv9B9+m3UP\nLRixdAEYm71Y/o/M3Ic+u8oH0vPWWm1spGjniT4lJ8VlTOTkMmLtHmptAoGAHSZS\n3Uoe6xY0krPLMwlBgRkkVpbZAVhnJeZqIgkLgqrhnwxMyqNLHuREvy1UNfP+maEL\n43vNbAcEFtoz0BT9sMlOI/UD6M8clc2nLMluRFGZ53mABXaA0zVduwbP/swe+o0o\nvc0p1kAT9MBPb5ZzlyK00D2dHgi7DZEkMZE9WpkCgYAwPZxHErWAr6JowF0Mbl5i\nm35ypc88p8Dt4HKoTlzfZnBnHMDI1Ht5SCXVAsGztW0CMgkCwMDZxUWWJiS+EWJ0\n0huyjTnSqR/zpUurBCWm1zLt9JYZ0mvOXy5EFSWxDo6yodK8+oHtgoXV8jguT91a\nMGgDGz/owPBaBtRO9KOe+w==\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-1imjv@meetingapp-27f7e.iam.gserviceaccount.com",
            "client_id": "107183285939664806188",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-1imjv%40meetingapp-27f7e.iam.gserviceaccount.com"
        }

    )
    firebase_admin.initialize_app(cred)


class PushView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        # init_app()
        api_key = "AAAAtiDoH2g:APA91bH1nQ-Oe9AZbYnEfhXRVuXyhGnyijaNcv-ZQmkVwuCHiTi0MTu5KWq_9f39QLmz4FZzjLbfxbeH0pg2Lh89y9M64_syQaH3q_HIck_qkGgY4xD2hymy6gD5K5YyseUfmxJNhSDl"
        push_service = FCMNotification(api_key=api_key)

        # OR initialize with proxies

        proxy_dict = {
            "http": "http://127.0.0.1",
            "https": "http://127.0.0.1",
        }
        push_service = FCMNotification(api_key=api_key, proxy_dict=proxy_dict)
        token = 'cBX5zV8BZdo:APA91bGCBWhvD-hHd3Nof6QRpwxqCr-FQKREkzUREEvmbb2rwJAScxeEY03ZXRNc8qjP-kubijTPKSYiuX2BnKC7brCNn1amrrQIH0PEgQd14AIgqTlpcla4RIhXxbE6J8lzDrYddkj8'

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

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get(request):
        events = Event.objects.filter(creator=request.user)
        serializer = EventSerializer(events.order_by('-id'), many=True)
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


class SendRequestView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            to_user = User.objects.get(id=self.request.data['to_user_id'])

            serializer.save(from_user=self.request.user, to_user=to_user)

            send_event_request(
                event_request=Request.objects.get(id=serializer.data['id'])
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


            # user=received_friend_request.from_user,
            # other_user=received_friend_request.to_user

        # send_created_friend_request(
        #     friend_request=friend_request,
        # )

        # serializer = RequestSerializer(data=request.data, many=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiveRequestView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            raise Http404

        # Accept a friend request from the user passed in to the 'username' query parameter

    def post(self, request, *args, **kwargs):
        # from_user = User.objects.get(id=16)
        # to_user = User.objects.get(id=15)
        # send_accepted_friend_request(
        #     user=from_user,
        #     other_user=to_user
        #     # user=received_friend_request.from_user,
        #     # other_user=received_friend_request.to_user
        # )

        return Response({'lala': 'alal'}, status=status.HTTP_201_CREATED)  # Created since we're creating a Friend

        # Reject a friend request from the user passed in to the 'username' query parameter

    def delete(self, request, *args, **kwargs):
        # received_friend_request = self.get_object()
        # received_friend_request.reject()
        #
        # send_rejected_friend_request(
        #     friend_request=received_friend_request
        # )
        #
        # serializer = self.serializer_class(received_friend_request)
        return Response({'1': '1'}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        my_request = self.get_object(pk)
        serializer = RequestSerializer(my_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
