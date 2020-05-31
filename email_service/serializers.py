from rest_framework.serializers import ModelSerializer

from .models import ConfirmationCode


class ConfirmationCodeSerializer(ModelSerializer):
    class Meta:
        model = ConfirmationCode
        fields = '__all__'

    def to_representation(self, obj):
        confirmation = super(ConfirmationCodeSerializer, self).to_representation(obj)
        confirmation.pop('id')

        return confirmation
