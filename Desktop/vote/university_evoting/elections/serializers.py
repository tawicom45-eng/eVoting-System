from rest_framework import serializers
from .models import Election, Position, Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ("id", "name", "manifesto", "approved")


class PositionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    class Meta:
        model = Position
        fields = ("id", "name", "candidates")


class ElectionSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        fields = ("id", "name", "description", "start_time", "end_time", "is_published", "positions")
