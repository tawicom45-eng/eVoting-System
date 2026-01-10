from rest_framework import serializers
from .models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ("id", "user", "election", "subject", "message", "status", "created_at")
        read_only_fields = ("id", "user", "status", "created_at")
