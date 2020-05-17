from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.models import Category
from .models import Ticket
from .serializers import TicketSerializer


class TicketListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def filter_events_by_user_roles(self, list_roles):
        q = Q()
        if list_roles:
            for role in list_roles:
                if role == 'creator':
                    q = q | Q(creator=self.request.user)

        else:
            q = ~Q(creator=self.request.user)

        return q

    @staticmethod
    def filter_events_by_categories(list_categories):
        if list_categories:
            categories = Category.objects.filter(name__in=list_categories).values_list('id', flat=True)
            return Q(categories__in=categories)
        else:
            return Q()

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        q = Q() | self.filter_events_by_user_roles(request.GET.getlist('me'))
        q = q & self.filter_events_by_categories(request.GET.getlist('category'))

        tickets = Ticket.objects.filter(q).distinct().order_by('-id')
        serializer = TicketSerializer(instance=tickets, many=True)

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
