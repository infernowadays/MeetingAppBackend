from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class CategoryListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        categories = Category.objects.all()

        data = list([])
        for category in categories:
            serializer = dict({})
            serializer['name'] = category.name
            serializer['categories'] = CategorySerializer(instance=category.sub_categories.all(), many=True).data
            data.append(serializer)

        return Response(data, status=status.HTTP_200_OK)


class FeedbackListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
