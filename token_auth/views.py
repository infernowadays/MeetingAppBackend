from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            first_name = self.request.data['name']
            username = self.request.data['login']
            password = self.request.data['password']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        if username is None or first_name is None or password is None:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        try:
            user = User.objects.create_user(username=username, first_name=first_name, password=password)
        except IntegrityError as e:
            return JsonResponse({'error': 'user exists'}, status=500, safe=False)

        return JsonResponse({'name': user.first_name, 'login': user.username}, status=200, safe=False)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            username = self.request.data['login']
            password = self.request.data['password']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        if username is None or password is None:
            return JsonResponse({'error': 'provide all the data'}, status=400)

        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'error': 'invalid credentials'}, status=404)
        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse({'token': token.key}, status=200, safe=False)


class EditProfileView(APIView):
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)

    def put(self):
        try:
            username = self.request.data['login']
            password = self.request.data['password']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        user = User.objects.get(username=username)
        user.username = username
        user.password = password
        user.save()

        return JsonResponse({'new username': user.username}, status=200, safe=False)
