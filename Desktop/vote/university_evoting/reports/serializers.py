from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "name", "generated_at", "file")
        read_only_fields = ("id", "generated_at")
