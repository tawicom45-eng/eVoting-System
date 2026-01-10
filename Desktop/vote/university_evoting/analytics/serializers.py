from rest_framework import serializers
from .models import Metric


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ["id", "name", "value", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]
