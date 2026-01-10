from rest_framework import serializers
from .models import PosterSubmission, PosterTemplate


class PosterSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosterSubmission
        fields = ('submission_id', 'candidate_user', 'candidate_name', 'candidate_position', 'slogan', 'photo', 'template', 'status', 'generated_files')
        read_only_fields = ('submission_id', 'status', 'generated_files')

    def validate_slogan(self, value):
        max_len = getattr(__import__('django.conf').conf.settings, 'POSTER_MAX_SLOGAN_LENGTH', 200)
        if value and len(value) > max_len:
            raise serializers.ValidationError('slogan too long')
        return value


class PosterTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosterTemplate
        fields = ('id', 'name', 'description', 'background_image')
