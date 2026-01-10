from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import VoteToken, EncryptedVote, QRLink


@admin.register(VoteToken)
class VoteTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "election", "token", "used")
    list_filter = ("used",)


@admin.register(EncryptedVote)
class EncryptedVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "position", "timestamp")
    readonly_fields = ("encrypted_payload",)


@admin.register(QRLink)
class QRLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "candidate", "created_at", "expires_at", "used")
    readonly_fields = ("token_hash", "created_at")
    actions = ["issue_signed_link"]

    def issue_signed_link(self, request, queryset):
        self.message_user(request, _("Use the 'Issue signed link' admin action from candidate admin instead."), level=messages.WARNING)
    issue_signed_link.short_description = _("Issue signed link")
