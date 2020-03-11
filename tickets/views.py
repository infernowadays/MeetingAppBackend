from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Ticket


class TicketsView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            name = self.request.data['name']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        try:
            user_id = Token.objects.get(key=key).user_id
        except Token.DoesNotExist:
            return JsonResponse({'error': 'token does not exist'}, status=404, safe=False)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'user does not exist'}, status=404, safe=False)

        ticket = Ticket.objects.create(name=name, creator=user)

        return JsonResponse({'id': ticket.id, 'name': ticket.name}, status=200, safe=False)

    @staticmethod
    def get(request):
        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        try:
            user_id = Token.objects.get(key=key).user_id
        except Token.DoesNotExist:
            return JsonResponse({'error': 'token does not exist'}, status=404, safe=False)

        tickets = Ticket.objects.filter(seller_id=user_id).values('id', 'name')
        return JsonResponse(list(tickets), status=200, safe=False)


class EditTicketView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def put(self):
        try:
            ticket_id = self.request.data['ticket_id']
            name = self.request.data['name']
            date = self.request.data['date']
            description = self.request.data['description']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        ticket = Ticket.objects.get(id=ticket_id)
        ticket.name = name
        ticket.date = date
        ticket.description = description
        ticket.save()

        return JsonResponse({'ticket was updated': ticket.description}, status=200, safe=False)
