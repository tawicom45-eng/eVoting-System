import io
import os
import tempfile
from unittest import mock

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posters import services
from posters.models import PosterSubmission


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PosterGenerationIntegrationTest(TestCase):
    def setUp(self):
        # create a temporary MEDIA_ROOT
        self.temp_media = tempfile.mkdtemp(prefix='test_media_')
        self.override = override_settings(MEDIA_ROOT=self.temp_media, SITE_URL='http://testserver')
        self.override.enable()

    def tearDown(self):
        self.override.disable()

    def _make_test_image_file(self):
        # create a small RGB PNG
        from PIL import Image
        img = Image.new('RGB', (800, 800), color='blue')
        b = io.BytesIO()
        img.save(b, format='PNG')
        b.seek(0)
        return SimpleUploadedFile('photo.png', b.read(), content_type='image/png')

    @mock.patch('posters.services.boto3.client')
    def test_generate_poster_and_uploads_to_s3(self, mock_boto_client):
        # Patch boto3 client to a fake object with upload_file and generate_presigned_url
        fake_s3 = mock.Mock()
        def upload_file(local, bucket, key):
            # simulate upload by checking file exists
            assert os.path.exists(local)

        def generate_presigned_url(op, Params, ExpiresIn):
            return f"https://s3.example.com/{Params['Key']}?expires={ExpiresIn}"

        fake_s3.upload_file.side_effect = upload_file
        fake_s3.generate_presigned_url.side_effect = generate_presigned_url
        mock_boto_client.return_value = fake_s3

        photo = self._make_test_image_file()

        submission = PosterSubmission.objects.create(
            candidate_name='Test Candidate',
            candidate_position='President',
            slogan='Vote for testing',
            photo=photo,
        )

        # call service directly
        result = services.generate_poster_files(submission)

        # should return presigned URLs for png and maybe pdf/qr
        self.assertIn('png', result)
        self.assertTrue(result['png'].startswith('https://'))
