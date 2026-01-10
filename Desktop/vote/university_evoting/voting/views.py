from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from .models import VoteToken, EncryptedVote
from .serializers import VoteTokenSerializer, EncryptedVoteSerializer, CastVoteSerializer
from .utils import simple_encrypt_vote
from elections.models import Election, Position, Candidate
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request


from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpResponseForbidden
from audit.models import AuditLog
from .utils_qr import generate_signed_qr_token, verify_signed_qr_token, token_hash
from .models import QRTokenUsage


class QRLandingView(View):
    """Public landing page for scanned QR codes. Shows candidate and prompts login/SSO."""

    def get(self, request, qr_slug):
        try:
            candidate = Candidate.objects.get(qr_slug=qr_slug)
        except Candidate.DoesNotExist:
            return render(request, 'voting/qr_not_found.html', status=404)

        # log the scan
        try:
            ip = request.META.get('REMOTE_ADDR')
            AuditLog.objects.create(user=None, action='qr.scan', meta=str({'candidate': candidate.pk, 'ip': ip}))
        except Exception:
            pass

        signed_token = request.GET.get('token')
        context = {'candidate': candidate, 'signed_token': signed_token}
        return render(request, 'voting/qr_landing.html', context)


@method_decorator(login_required, name='dispatch')
class QRConfirmView(View):
    """Confirmation page (requires login) for casting via QR. Supports optional signed token auto-cast."""

    def get(self, request, qr_slug):
        try:
            candidate = Candidate.objects.get(qr_slug=qr_slug)
        except Candidate.DoesNotExist:
            return render(request, 'voting/qr_not_found.html', status=404)

        signed_token = request.GET.get('token')
        auto_cast = False
        token_obj = None
        if signed_token:
            try:
                payload = verify_signed_qr_token(signed_token)
                # Ensure token is for this candidate and the user matches
                if payload.get('u') == request.user.id and payload.get('c') == candidate.id:
                    # prevent replay
                    th = token_hash(signed_token)
                    if not QRTokenUsage.objects.filter(token_hash=th).exists():
                        auto_cast = True
                        token_obj = th
            except Exception:
                auto_cast = False

        if auto_cast:
            # perform cast immediately
            return self._do_cast(request, candidate, token_hash_value=token_obj)

        return render(request, 'voting/qr_confirm.html', {'candidate': candidate, 'signed_token': signed_token})

    def post(self, request, qr_slug):
        try:
            candidate = Candidate.objects.get(qr_slug=qr_slug)
        except Candidate.DoesNotExist:
            return render(request, 'voting/qr_not_found.html', status=404)
        return self._do_cast(request, candidate)

    def _do_cast(self, request, candidate, token_hash_value=None):
        user = request.user
        from abac.policy import evaluate
        if not evaluate(user, action='cast_vote'):
            AuditLog.objects.create(user=user, action='qr.cast_failure', meta=str({'candidate': candidate.pk, 'reason': 'abac_deny'}))
            return HttpResponseForbidden('Not eligible to vote')

        election = candidate.position.election
        token_obj, _ = VoteToken.objects.get_or_create(user=user, election=election)
        if token_obj.used:
            AuditLog.objects.create(user=user, action='qr.cast_failure', meta=str({'candidate': candidate.pk, 'reason': 'token_used'}))
            return HttpResponseForbidden('Token already used')

        encrypted = simple_encrypt_vote(candidate.id, str(token_obj.token))
        signature = None
        try:
            from . import crypto
            signature = crypto.sign_with_tally_private(encrypted.encode('utf-8'))
        except Exception:
            signature = None

        ev = EncryptedVote.objects.create(election=election, position=candidate.position, candidate=candidate, encrypted_payload=encrypted, signature=signature)
        token_obj.used = True
        token_obj.save()

        # mark signed token as used to prevent replay
        if token_hash_value:
            try:
                QRTokenUsage.objects.create(token_hash=token_hash_value, user=user, candidate=candidate)
            except Exception:
                pass

        AuditLog.objects.create(user=user, action='qr.cast_success', meta=str({'candidate': candidate.pk, 'vote_id': ev.pk}))
        return redirect(reverse('voting-qr-success'))


def qr_success(request):
    return render(request, 'voting/qr_success.html')


class QRCastView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request, qr_slug):
        # Ensure authenticated (some test clients may not trigger DRF auth automatically)
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # Find candidate by qr_slug
        try:
            candidate = Candidate.objects.get(qr_slug=qr_slug)
        except Candidate.DoesNotExist:
            return Response({"detail": "Invalid QR code"}, status=status.HTTP_404_NOT_FOUND)

        # ABAC check for casting
        from abac.policy import evaluate
        if not evaluate(request.user, action="cast_vote", resource=None):
            return Response({"detail": "User not eligible to vote"}, status=status.HTTP_403_FORBIDDEN)

        # Ensure a VoteToken exists for this user and election
        election = candidate.position.election
        token_obj, _ = VoteToken.objects.get_or_create(user=request.user, election=election)
        if token_obj.used:
            return Response({"detail": "Token already used"}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed to cast vote for candidate
        encrypted = simple_encrypt_vote(candidate.id, str(token_obj.token))
        signature = None
        try:
            from . import crypto
            signature = crypto.sign_with_tally_private(encrypted.encode("utf-8"))
        except Exception:
            signature = None

        ev = EncryptedVote.objects.create(
            election=election,
            position=candidate.position,
            candidate=candidate,
            encrypted_payload=encrypted,
            signature=signature,
        )
        token_obj.used = True
        token_obj.save()
        out = EncryptedVoteSerializer(ev)
        return Response(out.data, status=status.HTTP_201_CREATED)


class IssueTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, election_id):
        # ABAC policy: check eligibility to issue token
        from abac.policy import evaluate
        if not evaluate(request.user, action="issue_token", resource=election_id):
            return Response({"detail": "User not eligible to receive voting token"}, status=status.HTTP_403_FORBIDDEN)

        election = get_object_or_404(Election, id=election_id)
        token_obj, created = VoteToken.objects.get_or_create(user=request.user, election=election)
        serializer = VoteTokenSerializer(token_obj)
        return Response(serializer.data)


class CastVoteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # ABAC policy: check eligibility to cast
        from abac.policy import evaluate
        if not evaluate(request.user, action="cast_vote", resource=None):
            return Response({"detail": "User not eligible to vote"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CastVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data["token"]
        position_id = serializer.validated_data["position_id"]
        candidate_id = serializer.validated_data["candidate_id"]

        token_obj = get_object_or_404(VoteToken, token=token_value, user=request.user)
        if token_obj.used:
            return Response({"detail": "Token already used"}, status=status.HTTP_400_BAD_REQUEST)

        position = get_object_or_404(Position, id=position_id, election=token_obj.election)
        candidate = get_object_or_404(Candidate, id=candidate_id, position=position)

        encrypted = simple_encrypt_vote(candidate_id, str(token_value))
        # sign the encrypted payload using tally signing key if present
        signature = None
        try:
            signature = crypto.sign_with_tally_private(encrypted.encode("utf-8"))
        except Exception:
            # no signing key present — signature left empty
            signature = None

        ev = EncryptedVote.objects.create(
            election=token_obj.election,
            position=position,
            candidate=candidate,
            encrypted_payload=encrypted,
            signature=signature,
        )
        token_obj.used = True
        token_obj.save()

        out = EncryptedVoteSerializer(ev)
        return Response(out.data, status=status.HTTP_201_CREATED)


class QRIssueView(APIView):
    """Endpoint for staff/admins to issue a signed QR token for a specific user and candidate.

    POST body: {"user_id": int, "candidate_id": int, "ttl_minutes": int (optional)}
    """
    permission_classes = (IsAdminUser,)

    def post(self, request):
        user_id = request.data.get('user_id')
        candidate_id = request.data.get('candidate_id')
        ttl = request.data.get('ttl_minutes')
        if not user_id or not candidate_id:
            return Response({'detail': 'user_id and candidate_id required'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            candidate = Candidate.objects.get(id=candidate_id)
        except Exception:
            return Response({'detail': 'user or candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        token = generate_signed_qr_token(user.id, candidate.id)
        th = token_hash(token)
        expires_at = None
        from django.utils import timezone
        if ttl:
            try:
                ttl_int = int(ttl)
                if ttl_int > 0:
                    expires_at = timezone.now() + timezone.timedelta(minutes=ttl_int)
            except Exception:
                pass

        from .models import QRLink
        q = QRLink.objects.create(token=token, token_hash=th, user=user, candidate=candidate, expires_at=expires_at)

        # construct preview URL
        signed_link = request.build_absolute_uri(reverse('voting-qr-landing', kwargs={'qr_slug': candidate.qr_slug})) + f"?token={token}"
        return Response({'token': token, 'token_hash': th, 'preview': signed_link}, status=status.HTTP_201_CREATED)


class QRVerifyView(APIView):
    """Verify a signed QR token (idempotent, safe). Public endpoint used by scanners/kiosks.

    POST body: {"token": "..."}
    """

    permission_classes = ()

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'token required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = verify_signed_qr_token(token)
        except Exception:
            return Response({'valid': False, 'reason': 'invalid_or_expired'}, status=status.HTTP_400_BAD_REQUEST)

        # check replay
        th = token_hash(token)
        if QRTokenUsage.objects.filter(token_hash=th).exists():
            return Response({'valid': False, 'reason': 'already_used'}, status=status.HTTP_400_BAD_REQUEST)

        # check candidate exists
        try:
            candidate = Candidate.objects.get(id=int(payload.get('c')))
        except Candidate.DoesNotExist:
            return Response({'valid': False, 'reason': 'candidate_not_found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'valid': True, 'candidate_id': candidate.id, 'candidate_name': candidate.name}, status=status.HTTP_200_OK)
