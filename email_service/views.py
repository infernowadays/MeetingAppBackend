from django.core.mail import EmailMessage
from django.http import Http404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from token_auth.models import UserProfile
from .models import ConfirmationCode
from .serializers import ConfirmationCodeSerializer
from .utils import generate_confirmation_code


class CheckConfirmationCodeView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            email = request.data['email']
            code = request.data['code']
        except KeyError:
            raise Http404

        user_profile = UserProfile.objects.filter(email=email)
        confirmation = ConfirmationCode.objects.filter(email=email)
        if not confirmation or not user_profile:
            raise Http404

        if code == confirmation[len(confirmation) - 1].code:
            user_profile.update(is_confirmed=True)
            return Response({}, status=status.HTTP_202_ACCEPTED)
        return Response({}, status=status.HTTP_406_NOT_ACCEPTABLE)


class GenerateConfirmationView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def send_email(to_email, code):
        mail_subject = 'Активция аккаунта WALK'
        message = 'Код активации: ' + str(code)

        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()

    def post(self, request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(code=generate_confirmation_code())

            self.send_email(to_email=serializer.data.get('email'), code=serializer.data.get('code'))

            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
