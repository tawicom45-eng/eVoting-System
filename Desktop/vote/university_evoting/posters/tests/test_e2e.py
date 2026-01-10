import io
import os
import tempfile
from unittest import mock

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posters.models import PosterSubmission
from posters import tasks


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PosterSubmissionE2ETest(TestCase):
    def setUp(self):
        self.temp_media = tempfile.mkdtemp(prefix='test_media_')
        self.override = override_settings(MEDIA_ROOT=self.temp_media, SITE_URL='http://testserver')
        self.override.enable()

    def tearDown(self):
        self.override.disable()

    def _make_test_image_file(self):
        from PIL import Image
        img = Image.new('RGB', (800, 800), color='green')
        b = io.BytesIO()
        img.save(b, format='PNG')
        b.seek(0)
        return SimpleUploadedFile('photo.png', b.read(), content_type='image/png')

    @mock.patch('posters.services.boto3.client')
    def test_submission_triggers_generation_and_writes_generated_files(self, mock_boto_client):
        fake_s3 = mock.Mock()
        fake_s3.upload_file.return_value = None
        fake_s3.generate_presigned_url.side_effect = lambda op, Params, ExpiresIn: f"https://s3.example.com/{Params['Key']}?e={ExpiresIn}"
        mock_boto_client.return_value = fake_s3

        photo = self._make_test_image_file()
        submission = PosterSubmission.objects.create(
            candidate_name='E2E Candidate',
            candidate_position='Secretary',
            slogan='E2E slogan',
            photo=photo,
        )

        # Call the Celery task directly (eager mode will run synchronously)
        tasks.generate_poster_task(submission_id=str(submission.submission_id))

        submission.refresh_from_db()
        self.assertTrue(submission.generated_files)
        self.assertIn('png', submission.generated_files)
