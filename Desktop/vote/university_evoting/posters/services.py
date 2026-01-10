import io
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import qrcode
from django.urls import reverse
import boto3
from botocore.exceptions import BotoCoreError, ClientError


DEFAULT_FONT_PATH = getattr(settings, 'POSTER_FONT_PATH', None)


def _load_font(size=40):
    try:
        if DEFAULT_FONT_PATH:
            return ImageFont.truetype(DEFAULT_FONT_PATH, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    cur = ''
    for w in words:
        test = cur + (' ' if cur else '') + w
        if draw.textsize(test, font=font)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return '\n'.join(lines)


def generate_qr_image(url, size=300):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size), Image.LANCZOS)
    return img


def compliance_check_submission(candidate_name, slogan, photo_path):
    """Basic compliance: check slogan length, banned words, photo size/format."""
    banned = getattr(settings, 'POSTER_BANNED_WORDS', [])
    max_slogan_len = getattr(settings, 'POSTER_MAX_SLOGAN_LENGTH', 200)
    errors = []
    if len(slogan or '') > max_slogan_len:
        errors.append('slogan_too_long')
    low = (slogan or '').lower()
    for b in banned:
        if b.lower() in low:
            errors.append('banned_word')
            break
    try:
        with Image.open(photo_path) as im:
            w, h = im.size
            if w < 300 or h < 300:
                errors.append('photo_too_small')
    except Exception:
        errors.append('invalid_photo')

    # Optional: use AWS Rekognition for NSFW / text detection if configured
    try:
        from django.conf import settings
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        use_rek = getattr(settings, 'POSTER_USE_REKOGNITION', False)
        if use_rek:
            rek = boto3.client('rekognition', region_name=getattr(settings, 'AWS_S3_REGION_NAME', None))
            with open(photo_path, 'rb') as f:
                img_bytes = f.read()
            try:
                resp = rek.detect_moderation_labels(Image={'Bytes': img_bytes}, MinConfidence=60)
                if resp.get('ModerationLabels'):
                    # consider any moderation label a failure for POC
                    errors.append('nsfw_detected')
            except Exception:
                # ignore rekognition failures, don't block submission
                pass
            try:
                # optional text detection for banned words
                txt = rek.detect_text(Image={'Bytes': img_bytes})
                detected = ' '.join([d.get('DetectedText', '') for d in txt.get('TextDetections', [])])
                low = (slogan or '').lower()
                for b in banned:
                    if b.lower() in detected.lower() or b.lower() in low:
                        errors.append('banned_word')
                        break
            except Exception:
                pass
    except Exception:
        pass

    return errors


def generate_poster_files(submission, template=None):
    """Generate PNG and PDF poster for a PosterSubmission instance.

    Returns dict with 'png' and 'pdf' filepaths and qr path.
    """
    media_root = settings.MEDIA_ROOT
    out_dir = os.path.join(media_root, 'posters', str(submission.submission_id))
    os.makedirs(out_dir, exist_ok=True)

    # Load base image: either template background or a plain canvas
    if template and template.background_image:
        base = Image.open(template.background_image.path).convert('RGB')
    else:
        base = Image.new('RGB', (2480, 3508), 'white')  # A4@300dpi approx

    draw = ImageDraw.Draw(base)
    width, height = base.size

    # Candidate photo: open, resize, and paste on left
    try:
        photo = Image.open(submission.photo.path).convert('RGB')
        ph = photo.copy()
        # target box
        box_w = int(width * 0.45)
        box_h = int(height * 0.6)
        ph.thumbnail((box_w, box_h), Image.LANCZOS)
        # center vertically
        x = int(width * 0.05)
        y = int((height - ph.size[1]) / 2)
        base.paste(ph, (x, y))
    except Exception:
        # ignore and continue
        pass

    # Draw candidate text on right
    font_title = _load_font(80)
    font_slogan = _load_font(48)
    text_x = int(width * 0.55)
    text_w = int(width * 0.4)
    y_cursor = int(height * 0.2)
    draw.text((text_x, y_cursor), submission.candidate_name, font=font_title, fill='black')
    y_cursor += 120
    # position
    draw.text((text_x, y_cursor), submission.candidate_position, font=_load_font(60), fill='black')
    y_cursor += 100
    # wrap slogan
    slogan_wrapped = _wrap_text(submission.slogan or '', font_slogan, text_w, draw)
    draw.multiline_text((text_x, y_cursor), slogan_wrapped, font=font_slogan, fill='black', spacing=8)

    # Generate QR code linking to candidate detail (if possible)
    try:
        url = submission.generated_files.get('detail_url') if submission.generated_files else None
        if not url:
            # try reverse lookup (best-effort; may require URL patterns)
            try:
                url = settings.SITE_URL.rstrip('/') + reverse('candidate-detail', kwargs={'submission_id': str(submission.submission_id)})
            except Exception:
                url = settings.SITE_URL.rstrip('/') + f"/posters/{submission.submission_id}/"
        qr_img = generate_qr_image(url, size=400)
        qr_x = int(width * 0.55)
        qr_y = int(height * 0.75)
        base.paste(qr_img, (qr_x, qr_y))
        # save qr to file
        qr_path = os.path.join(out_dir, 'qr.png')
        qr_img.save(qr_path, format='PNG')
    except Exception:
        qr_path = None

    # Save PNG
    png_path = os.path.join(out_dir, 'poster.png')
    base.save(png_path, format='PNG')

    # Save PDF (simple conversion)
    pdf_path = os.path.join(out_dir, 'poster.pdf')
    try:
        base.save(pdf_path, format='PDF')
    except Exception:
        # fallback: create a simple one-page PDF via reportlab if available
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(pdf_path, pagesize=A4)
            c.drawImage(png_path, 0, 0, width=A4[0], height=A4[1])
            c.showPage()
            c.save()
        except Exception:
            pdf_path = None

    result = {'png': png_path, 'pdf': pdf_path, 'qr': qr_path}

    # If S3 is configured, upload files and return presigned URLs instead of local paths
    try:
        from django.conf import settings
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        if bucket:
            s3 = boto3.client('s3', region_name=getattr(settings, 'AWS_S3_REGION_NAME', None))
            uploaded = {}
            for key_name, local_path in [('png', png_path), ('pdf', pdf_path), ('qr', qr_path)]:
                if not local_path:
                    continue
                object_key = f"posters/{submission.submission_id}/{key_name}{os.path.splitext(local_path)[1]}"
                try:
                    s3.upload_file(local_path, bucket, object_key)
                    # generate presigned URL valid for configurable period (default 7 days)
                    expires = int(getattr(settings, 'POSTER_PRESIGNED_URL_EXPIRES', 60 * 60 * 24 * 7))
                    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': object_key}, ExpiresIn=expires)
                    uploaded[key_name] = url
                except (BotoCoreError, ClientError):
                    # fall back to local path if upload fails
                    uploaded[key_name] = local_path
            result = uploaded
    except Exception:
        # if boto3 not configured or upload fails, return local paths
        pass

    return result
