from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import Report, ResultPublication


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "generated_at")
    readonly_fields = ("generated_at",)


@admin.register(ResultPublication)
class ResultPublicationAdmin(admin.ModelAdmin):
    list_display = ("election", "status", "reviewed_by", "published_by", "reviewed_at", "published_at")
    actions = ["mark_as_reviewed", "publish_results"]
    readonly_fields = ("created_at", "updated_at")

    def mark_as_reviewed(self, request, queryset):
        if not request.user.has_perm("reports.can_review_publication"):
            self.message_user(request, _("You do not have permission to mark publications as reviewed."), level=messages.ERROR)
            return
        count = 0
        for pub in queryset:
            if pub.status != pub.STATUS_DRAFT:
                continue
            pub.mark_reviewed(request.user)
            count += 1
        self.message_user(request, _("Marked %(count)d publication(s) as reviewed") % {"count": count})
    mark_as_reviewed.short_description = _("Mark selected publications as reviewed")

    def publish_results(self, request, queryset):
        if not request.user.has_perm("reports.can_publish_publication"):
            self.message_user(request, _("You do not have permission to publish publications."), level=messages.ERROR)
            return
        count = 0
        for pub in queryset:
            try:
                pub.publish(request.user)
                count += 1
            except Exception as e:
                self.message_user(request, _(str(e)), level=messages.ERROR)
        self.message_user(request, _("Published %(count)d publication(s)") % {"count": count})
    publish_results.short_description = _("Publish selected reviewed publications")
