from django import forms
from data.models import RadiosondeMeasurement, WeatherMeasurement, MeasuringDevice
from django.forms.widgets import SelectDateWidget
from datetime import date, time
from visuo_open_source.widgets import SelectTimeWidget, ColumnCheckboxSelectMultiple

class WeatherMeasurementForm(forms.Form):
    """
    Form to download weather measurements
    """
    
    def __init__(self,*args,**kwargs):
        super(WeatherMeasurementForm,self).__init__(*args,**kwargs)
        if MeasuringDevice.objects.filter(type = 'S').exists() & WeatherMeasurement.objects.exists():
            
            firstdate = WeatherMeasurement.objects.values_list('date', flat=True).order_by('date').first()
            self.fields['start_date_weather'].initial = firstdate
            self.fields['end_date_weather'].initial = date.today()
            
            measuring_device_values = [(device.id, device) for device in MeasuringDevice.objects.all() if device.type == 'S']
            self.fields['measuring_device_weather'].choices = measuring_device_values
            self.fields['measuring_device_weather'].initial = [c[0] for c in measuring_device_values]
    
    YEARS = range(date.today().year-10, date.today().year+1)
    start_date_weather = forms.DateField(label = 'Start date', widget = SelectDateWidget(years = YEARS))
    end_date_weather = forms.DateField(label = 'End date', widget = SelectDateWidget(years = YEARS))
    
    start_time_weather = forms.TimeField(label = 'Start time', widget=SelectTimeWidget(), initial = time(0,0,0,0))
    end_time_weather = forms.TimeField(label = 'End time', widget=SelectTimeWidget(), initial = time(23,59,59))

    measuring_device_weather = forms.ChoiceField(label = 'Device')
    
    fields_values = [('temperature', 'Temperature (C)'), 
                     ('humidity', 'Humidity (%)'), 
                     ('dew_point', 'Dew point (C)'), 
                     ('wind_speed', 'Wind speed (m/s)'), 
                     ('wind_direction', 'Wind direction (deg)'),
                     ('pressure', 'Pressure (hPa)'), 
                     ('rainfall_rate', 'Rainfall rate (mm/hr)'), 
                     ('solar_radiation', 'Solar radiation (W/m2)'), 
                     ('uv_index', 'UV Index')]
    fields_weather = forms.MultipleChoiceField(fields_values, label = 'Fields', widget = ColumnCheckboxSelectMultiple(columns=1, css_class="inner-table-1"), initial = [c[0] for c in fields_values])
        
    def clean(self):
        """
        Adding check on the dates and the number of rows to the data cleaning
        """
        
        cleaned_data = super(WeatherMeasurementForm, self).clean()

        start_date = cleaned_data.get("start_date_weather")
        end_date = cleaned_data.get("end_date_weather")
        start_time = cleaned_data.get("start_time_weather")
        end_time = cleaned_data.get("end_time_weather")
        measuring_device = cleaned_data.get("measuring_device_weather")

        err = False
        if start_date is not None and end_date is not None and start_time is not None and end_time is not None:
            if end_date < start_date:
                err = True
                raise forms.ValidationError("End date must be after start date.")
            if end_time < start_time:
                err = True
                raise forms.ValidationError("End time must be after start time.")
        else:
            err = True
            
        if not err:
            nbRes = WeatherMeasurement.objects.filter(date__gte = start_date, date__lte = end_date, time__gte = start_time, time__lte = end_time, device__in = measuring_device).count()
            if nbRes < 1:
                raise forms.ValidationError("No entry in the database.")
            
            if nbRes > 50000:
                raise forms.ValidationError("Max. number of entries (50'000) reached.")
                
        return cleaned_data
    

class RadiosondeMeasurementForm(forms.Form):
    """
    Form to download radiosonde measurements
    """
    
    def __init__(self,*args,**kwargs):
        super(RadiosondeMeasurementForm,self).__init__(*args,**kwargs)
        
        if MeasuringDevice.objects.filter(type = 'R').exists() & RadiosondeMeasurement.objects.exists():
            firstdate = RadiosondeMeasurement.objects.values_list('date', flat=True).order_by('date').first()
            self.fields['start_date_radiosonde'].initial = firstdate
            self.fields['end_date_radiosonde'].initial = date.today()
    
    YEARS = range(date.today().year-10, date.today().year+1)
    start_date_radiosonde = forms.DateField(label = 'Start date', widget = SelectDateWidget(years = YEARS))
    end_date_radiosonde = forms.DateField(label = 'End date', widget = SelectDateWidget(years = YEARS))
    
    time_values = [('AM', 'Morning'), ('PM', 'Afternoon')]
    time_radiosonde = forms.MultipleChoiceField(time_values, label = 'Time', widget = ColumnCheckboxSelectMultiple(columns=2, css_class="inner-table-2"), initial = [c[0] for c in time_values])
    
    fields_values = [('pressure', 'Atmospheric pressure (hPa)'), ('height', 'Geopotential height (m)'), ('temperature', 'Temperature (C)'), ('dew_point', 'Dewpoint temperature (C)'), ('rel_humidity', 'Relative humidity (%)'), ('wind_direction', 'Wind direction (deg)'), ('wind_speed', 'Wind speed (m/s)')]
    fields_radiosonde = forms.MultipleChoiceField(fields_values, label = 'Fields', widget = ColumnCheckboxSelectMultiple(columns=1, css_class="inner-table-1"), initial = [c[0] for c in fields_values])
    
    def clean_time_radiosonde(self):
        data = self.cleaned_data['time_radiosonde']
        if data is None:
            raise forms.ValidationError("Minimum one field is required.")
        return data
    
    def clean(self):
        """
        Adding check on the dates and the number of rows to the data cleaning
        """

        cleaned_data = super(RadiosondeMeasurementForm, self).clean()
        
        start = cleaned_data.get("start_date_radiosonde")
        end = cleaned_data.get("end_date_radiosonde")
        time = cleaned_data.get("time_radiosonde")

        if start is not None and end is not None:
            if end < start:
                raise forms.ValidationError("End date must be after start date.")
            elif time is not None:
                nbRes = RadiosondeMeasurement.objects.filter(date__gte = start, date__lte = end, time__in = time).count()
                if nbRes < 1:
                    raise forms.ValidationError("No entry in the database.")
                
                if nbRes > 50000:
                    raise forms.ValidationError("Max. number of entries (50'000) reached.")
        
        return cleaned_data
