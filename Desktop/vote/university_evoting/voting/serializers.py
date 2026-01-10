from rest_framework import serializers
from .models import VoteToken, EncryptedVote


class VoteTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteToken
        fields = ("id", "user", "election", "token", "used")
        read_only_fields = ("id", "user", "token", "used")


class EncryptedVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedVote
        fields = ("id", "election", "position", "candidate", "encrypted_payload", "timestamp")
        read_only_fields = ("id", "encrypted_payload", "timestamp")


class CastVoteSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    position_id = serializers.IntegerField()
    candidate_id = serializers.IntegerField()
