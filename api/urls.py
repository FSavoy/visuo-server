from django.conf.urls import url, include
from rest_framework.generics import CreateAPIView
from api.serializers import WeatherMeasurementSerializer, SkyPictureSerializer
from data.models import SkyPicture, WeatherMeasurement

urlpatterns = [
    url(r'^skypicture/', CreateAPIView.as_view(queryset = SkyPicture.objects.all(), serializer_class = SkyPictureSerializer)),
    url(r'^weathermeasurement/', CreateAPIView.as_view(queryset = WeatherMeasurement.objects.all(), serializer_class = WeatherMeasurementSerializer)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]