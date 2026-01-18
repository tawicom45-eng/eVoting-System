import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Post
from .serializers import UserSerializer, PostSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Class: function"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def get_user_posts(self, request, pk=None):
                logger.debug("Function called")
"""Function: function"""
try:
            user = self.get_object()
    except Exception as e:
        raise ValueError(f"Error in function: {e}")