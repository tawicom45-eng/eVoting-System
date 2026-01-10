from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from django.conf import settings


def get_webauthn_server():
    rp_id = getattr(settings, 'WEBAUTHN_RP_ID', None) or getattr(settings, 'DOMAIN', 'localhost')
    rp_name = getattr(settings, 'WEBAUTHN_RP_NAME', 'University E-Voting')
    rp = PublicKeyCredentialRpEntity(name=rp_name, id=rp_id)
    server = Fido2Server(rp)
    return server
