from data.models import SkyPicture, WeatherMeasurement, MeasuringDevice
from rest_framework import serializers
from django.core.files import File
import datetime
from fractions import Fraction
import exifread
from data.tasks import gator, computeProjection


class SkyPictureSerializer(serializers.Serializer):
    """
    Serializer to upload a sky picture. Reads the related fields from the EXIF metadata.
    """
    
    image = serializers.ImageField(required = False);
    
    def create(self, validated_data):
        
        instance = SkyPicture()
            
        image = validated_data['image']
        f = open(image.temporary_file_path(), 'rb+');
        
        # The corresponding device is inferred from the username
        request = self.context.get('request', None)
        try:
            station = MeasuringDevice.objects.get(username = request.user)
        except:
            raise serializers.ValidationError("You are not a whole sky imager")
        if station.type != "W":
            raise serializers.ValidationError("You are not a whole sky imager")
        instance.device = station
        
        # Reading the EXIF metadata
        try:
            tags = exifread.process_file(f)
            
            instance.exposure_time = str(float(Fraction(str(tags['EXIF ExposureTime']))))
            instance.aperture_value =  str(float(Fraction(str(tags['EXIF FNumber']))))
            instance.ISO_speed =  int(str(tags['EXIF ISOSpeedRatings']))
            
            dt = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
            instance.date = dt.date()
            instance.time = dt.time()
            instance.datetime = datetime.datetime.combine(instance.date, instance.time)
        except:
            raise serializers.ValidationError("Missing EXIF metadata")
        
        filename = dt.strftime("%Y-%m-%d-%H-%M-%S-") + station.username.username + ".jpg"
        
        instance.image.save(filename, File(f), False)
        
        # Undistorted image to be computed later
        instance.undistorted = 'undistorted/TODO.png'
        instance.save()
        
        # Initialize a separate thread to compute the undistortion
        gator.task(computeProjection, instance.id)

        return instance
        
class WeatherMeasurementSerializer(serializers.Serializer):
    """
    Serializer to upload a weather station measurement.
    """
    
    date = serializers.CharField(label = "Date (YYYY-mm-dd)")
    time = serializers.CharField(label = "Time (HH:MM:SS)")
    temperature = serializers.CharField(allow_null = True)
    humidity = serializers.CharField(allow_null = True)
    dew_point = serializers.CharField(allow_null = True)
    wind_speed = serializers.CharField(allow_null = True)
    wind_direction = serializers.CharField(allow_null = True)
    pressure = serializers.CharField(allow_null = True)
    rainfall_rate = serializers.CharField(allow_null = True)
    solar_radiation = serializers.CharField(allow_null = True)
    uv_index = serializers.CharField(allow_null = True)
    
        
    def update(self, instance, validated_data):

        return instance
    
    def create(self, validated_data):
        instance = WeatherMeasurement()
        
        # The corresponding device is inferred from the username
        request = self.context.get('request', None)
        try:
            station = MeasuringDevice.objects.get(username = request.user)
        except:
            raise serializers.ValidationError("You are not a weather station")
        if station.type != 'S':
            raise serializers.ValidationError("You are not a weather station")
            
        instance.device = station
        instance.date = datetime.datetime.strptime(validated_data.get('date'), "%Y-%m-%d").date()
        instance.time = datetime.datetime.strptime(validated_data.get('time'), "%H:%M:%S").time()
        instance.datetime = datetime.datetime.combine(instance.date, instance.time)
        instance.temperature = self.floatToString(validated_data.get('temperature'))
        instance.humidity = self.floatToString(validated_data.get('humidity'))
        instance.dew_point = self.floatToString(validated_data.get('dew_point'))
        instance.wind_speed = self.floatToString(validated_data.get('wind_speed'))
        instance.wind_direction = self.floatToString(validated_data.get('wind_direction'))
        instance.pressure = self.floatToString(validated_data.get('pressure'))
        instance.rainfall_rate = self.floatToString(validated_data.get('rainfall_rate'))
        instance.solar_radiation = self.floatToString(validated_data.get('solar_radiation'))
        instance.uv_index = self.floatToString(validated_data.get('uv_index'))
        
        instance.save()

        return instance
    
    def floatToString(self, inputStr):
        """
        Helper function to convert a float to a string or None if not a float
        """
        
        try:
            value = float(inputStr)
        except (ValueError, TypeError):
            value = None
        return value
    