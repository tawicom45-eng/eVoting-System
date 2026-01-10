from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer


class ReportListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Report.objects.all().order_by("-generated_at")
    serializer_class = ReportSerializer
