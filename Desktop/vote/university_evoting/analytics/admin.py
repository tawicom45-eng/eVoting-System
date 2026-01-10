from django.contrib import admin
from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "recorded_at")
    list_filter = ("name",)
    search_fields = ("name",)
