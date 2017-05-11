from django import forms
from datetime import date
from django.forms.widgets import SelectDateWidget
from data.models import SkyPicture, MeasuringDevice

class DateStationForm(forms.Form):
    """
    Form to choose date and weather station
    """
    
    def __init__(self,*args,**kwargs):
        super(DateStationForm,self).__init__(*args,**kwargs)
        station_values = [(device.id, device) for device in MeasuringDevice.objects.all() if device.type == 'S']
        device_values = [(device.id, device) for device in MeasuringDevice.objects.all() if ((device.type == 'W') and SkyPicture.objects.filter(device = device).exists())]
        self.fields['station'].choices = station_values
        self.fields['imager'].choices = device_values
    
    YEARS = range(date.today().year-10, date.today().year+1)
    
    date = forms.DateField(widget = SelectDateWidget(years = YEARS), initial=date.today())    
    station = forms.ChoiceField()
    imager = forms.ChoiceField()
    
    
class DateForm(forms.Form):
    """
    Form to choose date (without weather station)
    """
    
    def __init__(self,*args,**kwargs):
        super(DateForm,self).__init__(*args,**kwargs)
        device_values = [(device.id, device) for device in MeasuringDevice.objects.all() if ((device.type == 'W') and SkyPicture.objects.filter(device = device).exists())]
        self.fields['imager'].choices = device_values
    
    YEARS = range(date.today().year-10, date.today().year+1)
    
    date = forms.DateField(widget = SelectDateWidget(years = YEARS), initial=date.today())
    imager = forms.ChoiceField()