from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Metric
from .serializers import MetricSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg


class MetricListView(generics.ListAPIView):
    """List metrics with optional ?name=<name> and optional time range filters."""

    permission_classes = (permissions.AllowAny,)
    serializer_class = MetricSerializer

    def get_queryset(self):
        qs = Metric.objects.all().order_by("-recorded_at")
        name = self.request.query_params.get("name")
        since = self.request.query_params.get("since")
        until = self.request.query_params.get("until")
        if name:
            qs = qs.filter(name=name)
        # Accept ISO datetime strings for since/until and parse them safely
        from django.utils.dateparse import parse_datetime
        if since:
            # Try parsing ISO datetime strings. Some clients may send + in the timezone as a literal
            # '+' which gets converted to space in URLs. If initial parse fails, try replacing spaces
            # back to '+' as a best-effort recovery.
            dt = parse_datetime(since)
            if dt is None and " " in since:
                dt = parse_datetime(since.replace(" ", "+"))
            if dt is not None:
                qs = qs.filter(recorded_at__gte=dt)
        if until:
            dt = parse_datetime(until)
            if dt is None and " " in until:
                dt = parse_datetime(until.replace(" ", "+"))
            if dt is not None:
                qs = qs.filter(recorded_at__lte=dt)
        return qs


class MetricAggregateView(generics.RetrieveAPIView):
    """Return simple aggregated stats (avg) for a given metric name and optional window."""

    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        if not name:
            return Response({"detail": "name required"}, status=400)
        window = request.query_params.get("window", None)
        qs = Metric.objects.filter(name=name)
        if window:
            # window in seconds
            try:
                seconds = int(window)
                start = timezone.now() - timedelta(seconds=seconds)
                qs = qs.filter(recorded_at__gte=start)
            except Exception:
                pass
        avg = qs.aggregate(Avg("value"))["value__avg"]
        return Response({"name": name, "avg": avg})
