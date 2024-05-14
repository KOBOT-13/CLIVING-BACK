from rest_framework import serializers
from .models import Page, Clip, Frame, Hold

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = '__all__'
class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = ['image']
class HoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hold
        fields = '__all__'