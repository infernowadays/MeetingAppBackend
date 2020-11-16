from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event
from token_auth.models import UserProfile
from .models import Complaint, UserProfileWarning
from .serializers import ComplaintSerializer, UserProfileWarningSerializer


class ComplaintListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = ComplaintSerializer(data=request.data)
        if serializer.is_valid():
            if request.data.get('content_type') == 'EVENT':
                try:
                    suspected = Event.objects.get(id=request.data.get('content_id')).creator
                except Event.DoesNotExist:
                    raise Http404
            elif request.data.get('content_type') == 'PROFILE':
                try:
                    suspected = UserProfile.objects.get(id=request.data.get('content_id'))
                except UserProfile.DoesNotExist:
                    raise Http404
            else:
                raise Http404

            serializer.save(supplier=self.request.user, suspected=suspected)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        complaints = Complaint.objects.filter(reviewed=False)
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComplaintDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        complaint = self.get_object(pk)
        serializer = ComplaintSerializer(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        complaint = self.get_object(pk)
        serializer = ComplaintSerializer(complaint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileWarningListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        serializer = UserProfileWarningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            user_profile = UserProfile.objects.get(id=serializer.data.get('user_profile'))
            if user_profile.warnings >= 3:
                user_profile.is_blocked = True
                user_profile.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileWarningDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def get_object(pk):
        try:
            return UserProfileWarning.objects.get(pk=pk)
        except UserProfileWarning.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        warnings = UserProfileWarning.objects.filter(user_profile_id=pk)
        serializer = UserProfileWarningSerializer(warnings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        warning = self.get_object(pk)
        warning.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
