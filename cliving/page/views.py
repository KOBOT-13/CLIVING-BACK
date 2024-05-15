from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Page, Video, Checkpoint, Frame, Hold
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer
from rest_framework import viewsets


# Create your views here.
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    # @action(detail = True, methods = ['post'])

class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all()
    serializer_class = CheckpointSerializer

class FrameViewSet(viewsets.ModelViewSet):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

class HoldViewSet(viewsets.ModelViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer


