from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django_thumbs.db.models import ImageWithThumbsField
import datetime


class DateManager(models.Manager):
    """
    Describes a custom model manager to look for objects closest to a certain query date.
    """
    
    def __init__(self):
        super(DateManager, self).__init__()
        
    def get_next(self, queryDate, device = 'all'):
        """Returns the first date with measurements following the query date.

        Args:
            queryDate: datetime.date 
            device: The device (MeasuringDevice instance) to restrict the query to, or 'all' 

        Returns:
            datetime.date or None
        """
        
        if device == 'all':
            thisFilter = self
        else:
            thisFilter = self.filter(device = device)
        
        if thisFilter.filter(date__gt = queryDate).order_by('date','time').exists():
            pic = thisFilter.filter(date__gt = queryDate).order_by('date','time')[0]
            return pic.date
        else:
            return None
    
      
    def get_previous(self, queryDate, device = 'all'):
        """Returns the last date with measurements before the query date.

        Args:
            queryDate: datetime.date 
            device: The device (MeasuringDevice instance) to restrict the query to, or 'all' 

        Returns:
            datetime.date or None
        """
        
        if device == 'all':
            thisFilter = self
        else:
            thisFilter = self.filter(device = device)
        
        if thisFilter.filter(date__lt = queryDate).order_by('-date','-time').exists():
            pic = thisFilter.filter(date__lt = queryDate).order_by('-date','-time')[0]
            return pic.date
        else:
            return None
            
            
    def get_closest_to(self, queryDate, device = 'all'):
        """Returns the closest date with measurements to the query date.

        Args:
            queryDate: datetime.date 
            device: The device (MeasuringDevice instance) to restrict the query to, or 'all' 

        Returns:
            datetime.date or None (if no measurements)
        """
        
        # Check if data exists on that day
        if device == 'all':
            thisFilter = self
        else:
            thisFilter = self.filter(device = device)
            
        if thisFilter.filter(date = queryDate).order_by('date','time').exists():
            return queryDate
        else:
            nextMeas = self.get_next(queryDate, device)
            prevMeas = self.get_previous(queryDate, device)
            
            if nextMeas and prevMeas: # Measurement both before and after the query date
                if nextMeas - queryDate > queryDate - prevMeas: # Comparing distances
                    return prevMeas
                else:
                    return nextMeas
            elif nextMeas: # Measurements only after the query date
                return nextMeas
            else: # Measurements only before the query date or None
                return prevMeas
        
            
    def last(self, device = 'all'):
        """Returns the last recorded measurement

        Args:
            device: The device (MeasuringDevice instance) to restrict the query to, or 'all' 

        Returns:
            object or None if no measurement
        """
        
        if device == 'all':
            thisFilter = self
        else:
            thisFilter = self.filter(device = device)
        
        if thisFilter.order_by('-date').exists():
            latestDayImg = thisFilter.order_by('-date')[0]
            return thisFilter.filter(date = latestDayImg.date).order_by('-time')[0]
        else:
            return None



class MeasuringDevice(models.Model):
    """
    Describes a measuring device with associated information. Linked to a User for authentication.
    """
    
    TYPE_CHOICES = (
        ('W', 'Whole Sky Imager'),
        ('S', 'Weather station'),
        ('R', 'Radiosonde')
    )
    type = models.CharField("Device type", max_length=1, choices=TYPE_CHOICES, default='W')
    
    name = models.CharField("Name of the device", max_length=30)
    username = models.OneToOneField(User) # The username used by the device to connect with the server
    location = models.PointField("Coordinates of the device", spatial_index=False, geography=True, null=True)
    location_description = models.CharField("Location of the device", max_length=100)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name + ' at ' + self.location_description


class SkyPicture(models.Model):
    """
    Describes a picture captured by a sky imager.
    """
    
    # Date and time of capture
    date = models.DateField("Date of capture", db_index = True)
    time = models.TimeField("Time of capture", db_index = True)
    
    # Stores the image with generated thumbnails
    image = ImageWithThumbsField("Image file", upload_to='sky_images/%Y/%m/%d', sizes=((125,125),(1000,667)))
    # Info at https://code.google.com/p/django-thumbs/
    
    # Undistorted version of the image to project on the map
    undistorted = models.ImageField("Undistorted image", upload_to='undistorted/')
    
    # Image parameters
    exposure_time = models.FloatField("Exposure time") # stored as the denominator only (1/x)
    aperture_value = models.FloatField("Aperture value")
    ISO_speed = models.IntegerField("ISO speed")
    
    device = models.ForeignKey('MeasuringDevice', limit_choices_to={'type': 'W'}, verbose_name="Measuring device used")
    
    objects = DateManager()
    
    def __unicode__(self):
        dt = datetime.datetime.combine(self.date, self.time)
        return dt.strftime('%Y-%m-%d %H:%M') + ' with ' + unicode(self.device)


class WeatherMeasurement(models.Model):
    """
    Describes a picture captured by a sky imager.
    """
    
    # Date and time of capture
    date = models.DateField("Date of capture", null=True, db_index = True)
    time = models.TimeField("Time of capture", null=True, db_index = True)
    datetime = models.DateTimeField("Date and time of capture", null=True, db_index = True) # Combined
    
    temperature = models.FloatField("Temperature (C)", null=True)
    humidity = models.FloatField("Humidity (%)", null=True)
    dew_point = models.FloatField("Dew point (C)", null=True)
    wind_speed = models.FloatField("Wind speed (m/s)", null=True)
    wind_direction = models.FloatField("Wind direction (deg)", null=True)
    pressure = models.FloatField("Pressure (hPa)", null=True)
    rainfall_rate = models.FloatField("Rainfall rate (mm/hr)", null=True)
    solar_radiation = models.FloatField("Solar radiation (W/m2)", null=True)
    uv_index = models.FloatField("UV Index", null=True)
    
    objects = DateManager()
    
    device = models.ForeignKey('MeasuringDevice', limit_choices_to={'type': 'S'}, verbose_name="Measuring device used")
    def __unicode__(self):
        return self.datetime.strftime('%Y-%m-%d %H:%M') + ' with ' + unicode(self.device)


class RadiosondeMeasurement(models.Model):
    """
    Describes a measurement taken by a radiosonde.
    """
    
    TIME_CHOICES = (
        ('AM', 'Morning observation'),
        ('PM', 'Afternoon observation'),
    )
    time = models.CharField("Time of the day", max_length=2, choices=TIME_CHOICES, default='AM')
    date = models.DateField("Date of capture", db_index = True)
    pressure = models.FloatField("Atmospheric pressure (hPa)", null=True)
    height = models.FloatField("Geopotential height (m)", null=True)
    temperature = models.FloatField("Temperature (C)", null=True)
    dew_point = models.FloatField("Dewpoint temperature (C)", null=True)
    rel_humidity = models.FloatField("Relative humidity (%)", null=True)
    wind_direction = models.FloatField("Wind direction (deg)", null=True)
    wind_speed = models.FloatField("Wind speed (m/s)", null=True)
    
    device = models.ForeignKey('MeasuringDevice', limit_choices_to={'type': 'R'}, verbose_name="Measuring device used")
    
    def __unicode__(self):
        return self.date.strftime('%Y-%m-%d') + ' ' + self.time + ' - ' + str(self.height) + ' m.'
    
    