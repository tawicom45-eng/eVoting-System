from rest_framework import serializers
from .models import ExternalIntegration


class ExternalIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalIntegration
        fields = ("id", "name", "config", "enabled")
        read_only_fields = ("id",)
