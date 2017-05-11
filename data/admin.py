from django.contrib.gis import admin

# Register your models here.

from models import SkyPicture, MeasuringDevice, WeatherMeasurement, RadiosondeMeasurement
from django.contrib.gis import forms

# Custom interface for selecting the location of devices
class MeasuringDeviceAdminForm(forms.ModelForm):
    location = forms.PointField(widget=forms.OSMWidget(attrs={
            'display_raw': True}))

class MeasuringDeviceAdmin(admin.GeoModelAdmin):
    form = MeasuringDeviceAdminForm
    
admin.site.register(SkyPicture)
admin.site.register(WeatherMeasurement)
admin.site.register(MeasuringDevice, MeasuringDeviceAdmin)
admin.site.register(RadiosondeMeasurement)