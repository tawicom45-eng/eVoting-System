from rest_framework import generics, permissions
from .models import Complaint
from .serializers import ComplaintSerializer


class ComplaintCreateView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ComplaintSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
