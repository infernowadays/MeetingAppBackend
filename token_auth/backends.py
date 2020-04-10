from django.contrib.auth import get_user_model, get_backends
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        model = get_user_model()
        try:
            user = model.objects.get(email=kwargs.get('email'))
        except model.DoesNotExist:
            return None
        else:
            if user.check_password(kwargs.get('password')):
                return user
        return None
