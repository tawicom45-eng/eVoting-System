from django.urls import path
from . import views

urlpatterns = [
    path("metrics/", views.MetricListView.as_view(), name="metrics-list"),
    path("metrics/aggregate/", views.MetricAggregateView.as_view(), name="metrics-aggregate"),
]
