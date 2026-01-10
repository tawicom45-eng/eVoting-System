from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Election, Position, Candidate


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "is_published")
    list_filter = ("is_published",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "election")


class IssueSignedLinkForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), required=True)
    ttl_minutes = forms.IntegerField(min_value=0, required=False, help_text="Optional TTL in minutes (0 = no expiry)")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "approved", "qr_slug")
    list_filter = ("approved",)
    actions = ["issue_signed_link_to_user"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:candidate_id>/issue_signed_link/', self.admin_site.admin_view(self.issue_signed_link_view), name='elections_candidate_issue_signed_link'),
        ]
        return custom_urls + urls

    def issue_signed_link_view(self, request, candidate_id):
        # Permission enforced by admin_view wrapper
        candidate = Candidate.objects.filter(id=candidate_id).first()
        if not candidate:
            self.message_user(request, "Candidate not found", level=messages.ERROR)
            return redirect('..')

        if request.method == 'POST':
            form = IssueSignedLinkForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                ttl_minutes = form.cleaned_data.get('ttl_minutes')
                from voting.utils_qr import generate_signed_qr_token, token_hash
                from voting.models import QRLink
                token = generate_signed_qr_token(user.id, candidate.id)
                th = token_hash(token)
                expires_at = None
                if ttl_minutes and ttl_minutes > 0:
                    expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
                QRLink.objects.create(token=token, token_hash=th, user=user, candidate=candidate, expires_at=expires_at)
                self.message_user(request, f"Issued signed link for {user.username} (candidate {candidate.name})", level=messages.SUCCESS)

                # Prepare a preview for the admin: absolute landing URL with token and a QR image
                signed_link = request.build_absolute_uri(reverse('voting-qr-landing', kwargs={'qr_slug': candidate.qr_slug})) + f"?token={token}"
                from urllib.parse import quote_plus
                qr_src = f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={quote_plus(signed_link)}"
                context = dict(
                    self.admin_site.each_context(request),
                    signed_link=signed_link,
                    qr_src=qr_src,
                    candidate=candidate,
                    user=user,
                )
                return render(request, 'admin/elections/issue_signed_link_result.html', context)
        else:
            form = IssueSignedLinkForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            candidate=candidate,
        )
        return render(request, 'admin/elections/issue_signed_link.html', context)

    def issue_signed_link_to_user(self, request, queryset):
        # Keep old action for backward compatibility but recommend using the interactive form
        self.message_user(request, ("Use the 'Issue signed link' admin button on the candidate change page for an interactive experience."), level=messages.WARNING)
    issue_signed_link_to_user.short_description = ("Issue signed link to user (interactive)")
