from django.urls import path
from .views import ComplaintCreateView

urlpatterns = [
    path("create/", ComplaintCreateView.as_view(), name="api-complaint-create"),
]
