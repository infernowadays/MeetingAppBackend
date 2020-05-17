from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.utils import *
from .models import Ticket
from .serializers import TicketSerializer


class TicketListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q() | not_requested_tickets(queryset=self.queryset, user=request.user)
        q = q & filter_by_user_roles(list_roles=request.GET.getlist('me'), user=request.user)
        q = q & filter_by_categories(request.GET.getlist('category'))

        tickets = self.queryset.filter(q).distinct().order_by('-id')
        serializer = self.serializer_class(instance=tickets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketDetailView(APIView):
    @staticmethod
    def get_object(pk):
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ticket = self.get_object(pk)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        ticket = self.get_object(pk)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = self.get_object(pk)
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
