from rest_framework import serializers
from .models import Profile, MFATOTPDevice, TrustedDevice


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "student_id", "role")
        read_only_fields = ("id", "user")


class MFATOTPRegisterSerializer(serializers.Serializer):
    label = serializers.CharField(required=False, allow_blank=True, max_length=100)


class MFATOTPVerifySerializer(serializers.Serializer):
    device_id = serializers.IntegerField()
    token = serializers.CharField(max_length=16)

    def validate(self, attrs):
        # Basic validation; detailed verification occurs in the view
        return attrs


class MFATOTPDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFATOTPDevice
        fields = ("id", "label", "confirmed", "created_at")
        read_only_fields = ("id", "confirmed", "created_at")


class TrustedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedDevice
        fields = ("id", "device_id", "name", "fingerprint", "trusted_until", "last_used", "revoked", "created_at")
        read_only_fields = ("id", "device_id", "last_used", "created_at")
