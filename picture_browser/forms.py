from django import forms
from data.models import SkyPicture
from datetime import date, time
from fractions import Fraction
from visuo_open_source.widgets import SelectTimeWidget, ColumnCheckboxSelectMultiple
from data.models import MeasuringDevice
from django.forms.widgets import SelectDateWidget


class SkyPictureQueryForm(forms.Form):
    """
    Form to filter the images
    """
    
    def __init__(self,*args,**kwargs):
        super(SkyPictureQueryForm,self).__init__(*args,**kwargs)
        
        # Initialize date selection fields
        firstdate = SkyPicture.objects.values_list('date', flat=True).order_by('date').first()
        self.fields['start_date'].initial = firstdate
        self.fields['end_date'].initial = date.today()
        
        # Initialize the choice of sky imager amongst all in the database
        measuring_device_values = [(device.id, device) for device in MeasuringDevice.objects.all() if device.type == 'W']
        self.fields['device'].choices = measuring_device_values
        
        # Initialize the exposure values amongst all available
        exposure_time_values = [];
        for elem in SkyPicture.objects.values_list('exposure_time', flat=True).distinct().order_by('exposure_time'):
            frac = Fraction(elem).limit_denominator(4000)
            exposure_time_values.append([str(elem), str(frac)])
        self.fields['exposure_time'].choices = exposure_time_values
        self.fields['exposure_time'].initial = [c[0] for c in exposure_time_values]
        
        # Initialize the aperture values amongst all available
        aperture_values = [];
        for elem in SkyPicture.objects.values_list('aperture_value', flat=True).distinct().order_by('aperture_value'):
            aperture_values.append([str(elem), 'f/'+str(elem)])
        self.fields['aperture_value'].choices = aperture_values
        self.fields['aperture_value'].initial = [c[0] for c in aperture_values]
        
        # Initialize the ISO values amongst all available
        ISO_speed_values = [];
        for elem in SkyPicture.objects.values_list('ISO_speed', flat=True).distinct().order_by('ISO_speed'):
            ISO_speed_values.append([str(elem), str(elem)])
        self.fields['ISO_speed'].choices = ISO_speed_values
        self.fields['ISO_speed'].initial = [c[0] for c in ISO_speed_values]
    
    # Date selection
    YEARS = range(date.today().year-10, date.today().year+1)
    start_date = forms.DateField(widget = SelectDateWidget(years = YEARS))
    end_date = forms.DateField(widget = SelectDateWidget(years = YEARS))
    
    start_time = forms.TimeField(widget=SelectTimeWidget(), initial = time(0,0,0,0))
    end_time = forms.TimeField(widget=SelectTimeWidget(), initial = time(23,59,59))
    
    device = forms.ChoiceField()
    
    exposure_time = forms.MultipleChoiceField(widget = ColumnCheckboxSelectMultiple(columns=3, css_class="inner-table"))
    aperture_value = forms.MultipleChoiceField(widget = ColumnCheckboxSelectMultiple(columns=3, css_class="inner-table"))
    ISO_speed = forms.MultipleChoiceField(widget = ColumnCheckboxSelectMultiple(columns=3, css_class="inner-table"))
    
