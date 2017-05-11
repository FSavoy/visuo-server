from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data.models import SkyPicture, WeatherMeasurement, RadiosondeMeasurement, MeasuringDevice
from forms import DateStationForm, DateForm
from django.shortcuts import redirect
from django.conf import settings
import numpy as np
import json

@login_required
# in case cannot see wsi, we redirect to the download page
def show_image(request, shift = 0):
    """
    Generates the visualization page, fetching all related data (images, weather and radiosonde)
    """
    
    # If there is no sky imager device installed, redirect towards the images part
    if not SkyPicture.objects.exists():
        return redirect('pictures/')
    
    # Check if the weather station form should be shown
    if WeatherMeasurement.objects.exists():
        weather = True
    else:
        weather = False
    
    args = {}
    args["title"] = "Data visualization"
    
    if request.POST or 'POST_map' in request.session:
        if request.POST:
            form_values = request.POST
            request.session['POST_map'] = form_values
        else:
            form_values = request.session['POST_map']
        
        if weather:
            form = DateStationForm(form_values)
        else:
            form = DateForm(form_values)
        
        if form.is_valid():
            queryDate = form.cleaned_data['date']
            device = MeasuringDevice.objects.get(id = form.cleaned_data['imager'])
            if not device.skypicture_set.all() > 0:
                device = [device for device in MeasuringDevice.objects.all() if ((device.type == 'W') and (len(device.skypicture_set.all()) > 0))][0]
            
            queryDate = SkyPicture.objects.get_closest_to(queryDate, device)
            if shift == '1':
                queryDateNew = SkyPicture.objects.get_next(queryDate, device)
                if queryDateNew:
                    queryDate = queryDateNew
            elif shift == '-1':
                queryDateNew = SkyPicture.objects.get_previous(queryDate, device)
                if queryDateNew:
                    queryDate = queryDateNew
                    
            if weather:
                station = MeasuringDevice.objects.get(id = form.cleaned_data['station'])
            
        else:
            device = [device for device in MeasuringDevice.objects.all() if ((device.type == 'W') and (len(device.skypicture_set.all()) > 0))][0]
            
            firstImage = SkyPicture.objects.filter(device = device).order_by('-date','-time')[0]
            queryDate = firstImage.date
            if weather:
                station = [station for station in MeasuringDevice.objects.all() if station.type == 'S'][0]
        
    else:
        form = DateStationForm()
        device = [device for device in MeasuringDevice.objects.all() if ((device.type == 'W') and (len(device.skypicture_set.all()) > 0))][0]
        firstImage = SkyPicture.objects.filter(device = device).order_by('-date','-time')[0]
        queryDate = firstImage.date
        if weather:
            station = [station for station in MeasuringDevice.objects.all() if station.type == 'S'][0]
    
    # Generating data for the new form with the actual retrieved data
    if weather:
        new_data = {'date': unicode(queryDate), 'station': station.id, 'imager': device.id}
        form = DateStationForm(new_data)
    else:
        new_data = {'date': unicode(queryDate), 'imager': device.id}
        form = DateForm(new_data)
        
    request.session['POST_map'] = new_data

    args['form'] = form
    args['longCtr'] = device.location.x
    args['latCtr'] = device.location.y
    
    # Check if there are images before or after to show Next or Previous buttons
    if SkyPicture.objects.get_next(queryDate, device):
        args['next'] = 1
    if SkyPicture.objects.get_previous(queryDate, device):
        args['previous'] = 1

    # 
    # Fetching images
    #
    
    imagesData = SkyPicture.objects.filter(device = device, date = queryDate).order_by('time')
    images = []
    for im in imagesData:
        thisIm = {}
        thisIm['url'] = im.image.url
        thisIm['url_tn'] = im.image.url.replace('.jpg', '.125x125.jpg')
        thisIm['undistorted'] = im.undistorted.url
        thisIm['time'] = im.time.strftime("%H:%M:%S")
        thisIm['id'] = str(im.id)
        images.append(thisIm)
    args['images'] = images
    
    
    # 
    # Fetching weather data 
    #
        
    temperature = []
    humidity = []
    dew_point = []
    wind_speed = []
    wind_direction = []
    pressure = []
    rainfall_rate = []
    solar_radiation = []
    uv_index = []
    cloud_height = []
    
    if not weather:
        args['boolWeather'] = False
    else:
        measurementsData = WeatherMeasurement.objects.filter(date = queryDate, device = station).order_by('time')
        if not measurementsData:
            args['boolWeather'] = False 
        else:
            args['boolWeather'] = True 
            
            for meas in measurementsData:
                if meas.temperature is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")
                    thisMeas['value'] = meas.temperature
                    temperature.append(thisMeas)
                if meas.humidity is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")
                    thisMeas['value'] = meas.humidity
                    humidity.append(thisMeas)
                if meas.dew_point is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")            
                    thisMeas['value'] = meas.dew_point
                    dew_point.append(thisMeas)
                if meas.wind_speed is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")            
                    thisMeas['value'] = meas.wind_speed
                    wind_speed.append(thisMeas)
                if meas.wind_direction is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")                        
                    thisMeas['value'] = meas.wind_direction
                    wind_direction.append(thisMeas)
                if meas.pressure is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")     
                    thisMeas['value'] = meas.pressure
                    pressure.append(thisMeas)
                if meas.rainfall_rate is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")   
                    thisMeas['value'] = meas.rainfall_rate
                    rainfall_rate.append(thisMeas)
                if meas.solar_radiation is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")   
                    thisMeas['value'] = meas.solar_radiation
                    solar_radiation.append(thisMeas)
                if meas.uv_index is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")  
                    thisMeas['value'] = meas.uv_index
                    uv_index.append(thisMeas)
                if meas.temperature is not None and meas.dew_point is not None:
                    thisMeas = {}
                    thisMeas['time'] = meas.time.strftime("%H:%M:%S")  
                    thisMeas['value'] = round(125*(meas.temperature - meas.dew_point),1)
                    cloud_height.append(thisMeas)
                    
    # Giving weather data (potentially empty) to the template
    args['temperature'] = temperature
    args['humidity'] = humidity
    args['dew_point'] = dew_point
    args['wind_speed'] = wind_speed
    args['wind_direction'] = wind_direction
    args['pressure'] = pressure
    args['rainfall_rate'] = rainfall_rate
    args['solar_radiation'] = solar_radiation
    args['uv_index'] = uv_index
    args['cloud_height'] = cloud_height
            
    # Items for the form
    items = []
    if temperature:
        items.append(('temperature', 'Temperature (deg. C)'))
    if humidity:
        items.append(('humidity', 'Humidity (%)'))
    if dew_point:
        items.append(('dew_point', 'Dew point (deg. C)'))
    if cloud_height:
        items.append(('cloud_height', 'Cloud base height (m.)'))
    if wind_speed:
        items.append(('wind_speed', 'Wind speed (m/s)'))
    if wind_direction:
        items.append(('wind_direction', 'Wind direction azimuth (deg.)'))
    if pressure:
        items.append(('pressure', 'Pressure (hPa)'))
    if rainfall_rate:
        items.append(('rainfall_rate', 'Rainfall rate (mm/hr)'))
    if solar_radiation:
        items.append(('solar_radiation', 'Solar radiation (W/m2)'))
    if uv_index:
        items.append(('uv_index', 'UV index'))
    args['items'] = json.dumps(items)
    
    
    # 
    # Fetching radiosonde data
    #
    
    altitudes = np.arange(0,18,0.01)
    radiosondeDataAM = RadiosondeMeasurement.objects.filter(date = queryDate).filter(time = 'AM').order_by('height')
    if not radiosondeDataAM:
        args['boolRadiosondeAM'] = False
        args['allValuesRadAM'] = []
        args['allSamplesRadAM'] = []
    else:
        args['boolRadiosondeAM'] = True
        allValuesRadAM = {};
        allSamplesRadAM = {};
        
        PRES_samples_AM = []
        PRES_heights_AM = np.empty(radiosondeDataAM.count())
        PRES_values_AM = np.empty(radiosondeDataAM.count())
        PRES_counter_AM = 0
        TEMP_samples_AM = []
        TEMP_heights_AM = np.empty(radiosondeDataAM.count())
        TEMP_values_AM = np.empty(radiosondeDataAM.count())
        TEMP_counter_AM = 0
        DWPT_samples_AM = []
        DWPT_heights_AM = np.empty(radiosondeDataAM.count())
        DWPT_values_AM = np.empty(radiosondeDataAM.count())
        DWPT_counter_AM = 0
        RELH_samples_AM = []
        RELH_heights_AM = np.empty(radiosondeDataAM.count())
        RELH_values_AM = np.empty(radiosondeDataAM.count())
        RELH_counter_AM = 0
        DRCT_samples_AM = []
        DRCT_heights_AM = np.empty(radiosondeDataAM.count())
        DRCT_values_AM = np.empty(radiosondeDataAM.count())
        DRCT_counter_AM = 0
        SKNT_samples_AM = []
        SKNT_heights_AM = np.empty(radiosondeDataAM.count())
        SKNT_values_AM = np.empty(radiosondeDataAM.count())
        SKNT_counter_AM = 0
        for rad in radiosondeDataAM:
            if rad.height:
                if rad.pressure:
                    PRES_samples_AM.append(rad.height)
                    PRES_heights_AM[PRES_counter_AM] = rad.height/1000
                    PRES_values_AM[PRES_counter_AM] = rad.pressure
                    PRES_counter_AM = PRES_counter_AM + 1
                if rad.temperature:
                    TEMP_samples_AM.append(rad.height)
                    TEMP_heights_AM[TEMP_counter_AM] = rad.height/1000
                    TEMP_values_AM[TEMP_counter_AM] = rad.temperature
                    TEMP_counter_AM = TEMP_counter_AM + 1
                if rad.dew_point:
                    DWPT_samples_AM.append(rad.height)
                    DWPT_heights_AM[DWPT_counter_AM] = rad.height/1000
                    DWPT_values_AM[DWPT_counter_AM] = rad.dew_point
                    DWPT_counter_AM = DWPT_counter_AM + 1
                if rad.rel_humidity:
                    RELH_samples_AM.append(rad.height)
                    RELH_heights_AM[RELH_counter_AM] = rad.height/1000
                    RELH_values_AM[RELH_counter_AM] = rad.rel_humidity
                    RELH_counter_AM = RELH_counter_AM + 1
                if rad.wind_direction:
                    DRCT_samples_AM.append(rad.height)
                    DRCT_heights_AM[DRCT_counter_AM] = rad.height/1000
                    DRCT_values_AM[DRCT_counter_AM] = rad.wind_direction
                    DRCT_counter_AM = DRCT_counter_AM + 1
                if rad.wind_speed:
                    SKNT_samples_AM.append(rad.height)
                    SKNT_heights_AM[SKNT_counter_AM] = rad.height/1000
                    SKNT_values_AM[SKNT_counter_AM] = rad.pressure
                    SKNT_counter_AM = SKNT_counter_AM + 1
                
        PRES_heights_AM.resize(len(PRES_samples_AM))
        PRES_values_AM.resize(len(PRES_samples_AM))
        allValuesRadAM['PRES'] = np.interp(altitudes, PRES_heights_AM, PRES_values_AM).tolist()
        allSamplesRadAM['PRES'] = PRES_samples_AM;
        
        TEMP_heights_AM.resize(len(TEMP_samples_AM))
        TEMP_values_AM.resize(len(TEMP_samples_AM))
        allValuesRadAM['TEMP'] = np.interp(altitudes, TEMP_heights_AM, TEMP_values_AM).tolist()
        allSamplesRadAM['TEMP'] = TEMP_samples_AM;
        
        DWPT_heights_AM.resize(len(DWPT_samples_AM))
        DWPT_values_AM.resize(len(DWPT_samples_AM))
        allValuesRadAM['DWPT'] = np.interp(altitudes, DWPT_heights_AM, DWPT_values_AM).tolist()
        allSamplesRadAM['DWPT'] = DWPT_samples_AM;
        
        RELH_heights_AM.resize(len(RELH_samples_AM))
        RELH_values_AM.resize(len(RELH_samples_AM))
        allValuesRadAM['RELH'] = np.interp(altitudes, RELH_heights_AM, RELH_values_AM).tolist()
        allSamplesRadAM['RELH'] = RELH_samples_AM;
        
        DRCT_heights_AM.resize(len(DRCT_samples_AM))
        DRCT_values_AM.resize(len(DRCT_samples_AM))
        allValuesRadAM['DRCT'] = np.interp(altitudes, DRCT_heights_AM, DRCT_values_AM).tolist()
        allSamplesRadAM['DRCT'] = DRCT_samples_AM;
        
        SKNT_heights_AM.resize(len(SKNT_samples_AM))
        SKNT_values_AM.resize(len(SKNT_samples_AM))
        allValuesRadAM['SKNT'] = np.interp(altitudes, SKNT_heights_AM, SKNT_values_AM).tolist()
        allSamplesRadAM['SKNT'] = SKNT_samples_AM;
        
        # Critical humidity function
        alpha = 1.0
        beta = np.sqrt(3)
        sigma = np.array(allValuesRadAM['PRES'])/allValuesRadAM['PRES'][0]
        chum = 1 - alpha*sigma*(1 - sigma)*(1+beta*(sigma - 0.5));
        allValuesRadAM['clouds'] = np.int_(np.array(allValuesRadAM['RELH']) > chum * 100).tolist()
        
        allValuesRadAM['HGHT'] = altitudes.tolist()
        args['allValuesRadAM'] = allValuesRadAM
        args['allSamplesRadAM'] = allSamplesRadAM
    
    
    
    radiosondeDataPM = RadiosondeMeasurement.objects.filter(date = queryDate).filter(time = 'PM').order_by('height')
    if not radiosondeDataPM:
        args['boolRadiosondePM'] = False
        args['allValuesRadPM'] = []
        args['allSamplesRadPM'] = []
    else:
        args['boolRadiosondePM'] = True
        allValuesRadPM = {};
        allSamplesRadPM = {};
        
        PRES_samples_PM = []
        PRES_heights_PM = np.empty(radiosondeDataPM.count())
        PRES_values_PM = np.empty(radiosondeDataPM.count())
        PRES_counter_PM = 0
        TEMP_samples_PM = []
        TEMP_heights_PM = np.empty(radiosondeDataPM.count())
        TEMP_values_PM = np.empty(radiosondeDataPM.count())
        TEMP_counter_PM = 0
        DWPT_samples_PM = []
        DWPT_heights_PM = np.empty(radiosondeDataPM.count())
        DWPT_values_PM = np.empty(radiosondeDataPM.count())
        DWPT_counter_PM = 0
        RELH_samples_PM = []
        RELH_heights_PM = np.empty(radiosondeDataPM.count())
        RELH_values_PM = np.empty(radiosondeDataPM.count())
        RELH_counter_PM = 0
        DRCT_samples_PM = []
        DRCT_heights_PM = np.empty(radiosondeDataPM.count())
        DRCT_values_PM = np.empty(radiosondeDataPM.count())
        DRCT_counter_PM = 0
        SKNT_samples_PM = []
        SKNT_heights_PM = np.empty(radiosondeDataPM.count())
        SKNT_values_PM = np.empty(radiosondeDataPM.count())
        SKNT_counter_PM = 0
        for rad in radiosondeDataPM:
            if rad.height:
                if rad.pressure:
                    PRES_samples_PM.append(rad.height)
                    PRES_heights_PM[PRES_counter_PM] = rad.height/1000
                    PRES_values_PM[PRES_counter_PM] = rad.pressure
                    PRES_counter_PM = PRES_counter_PM + 1
                if rad.temperature:
                    TEMP_samples_PM.append(rad.height)
                    TEMP_heights_PM[TEMP_counter_PM] = rad.height/1000
                    TEMP_values_PM[TEMP_counter_PM] = rad.temperature
                    TEMP_counter_PM = TEMP_counter_PM + 1
                if rad.dew_point:
                    DWPT_samples_PM.append(rad.height)
                    DWPT_heights_PM[DWPT_counter_PM] = rad.height/1000
                    DWPT_values_PM[DWPT_counter_PM] = rad.dew_point
                    DWPT_counter_PM = DWPT_counter_PM + 1
                if rad.rel_humidity:
                    RELH_samples_PM.append(rad.height)
                    RELH_heights_PM[RELH_counter_PM] = rad.height/1000
                    RELH_values_PM[RELH_counter_PM] = rad.rel_humidity
                    RELH_counter_PM = RELH_counter_PM + 1
                if rad.wind_direction:
                    DRCT_samples_PM.append(rad.height)
                    DRCT_heights_PM[DRCT_counter_PM] = rad.height/1000
                    DRCT_values_PM[DRCT_counter_PM] = rad.wind_direction
                    DRCT_counter_PM = DRCT_counter_PM + 1
                if rad.wind_speed:
                    SKNT_samples_PM.append(rad.height)
                    SKNT_heights_PM[SKNT_counter_PM] = rad.height/1000
                    SKNT_values_PM[SKNT_counter_PM] = rad.pressure
                    SKNT_counter_PM = SKNT_counter_PM + 1
                
        PRES_heights_PM.resize(len(PRES_samples_PM))
        PRES_values_PM.resize(len(PRES_samples_PM))
        allValuesRadPM['PRES'] = np.interp(altitudes, PRES_heights_PM, PRES_values_PM).tolist()
        allSamplesRadPM['PRES'] = PRES_samples_PM;
        
        TEMP_heights_PM.resize(len(TEMP_samples_PM))
        TEMP_values_PM.resize(len(TEMP_samples_PM))
        allValuesRadPM['TEMP'] = np.interp(altitudes, TEMP_heights_PM, TEMP_values_PM).tolist()
        allSamplesRadPM['TEMP'] = TEMP_samples_PM;
        
        DWPT_heights_PM.resize(len(DWPT_samples_PM))
        DWPT_values_PM.resize(len(DWPT_samples_PM))
        allValuesRadPM['DWPT'] = np.interp(altitudes, DWPT_heights_PM, DWPT_values_PM).tolist()
        allSamplesRadPM['DWPT'] = DWPT_samples_PM;
        
        RELH_heights_PM.resize(len(RELH_samples_PM))
        RELH_values_PM.resize(len(RELH_samples_PM))
        allValuesRadPM['RELH'] = np.interp(altitudes, RELH_heights_PM, RELH_values_PM).tolist()
        allSamplesRadPM['RELH'] = RELH_samples_PM;
        
        DRCT_heights_PM.resize(len(DRCT_samples_PM))
        DRCT_values_PM.resize(len(DRCT_samples_PM))
        allValuesRadPM['DRCT'] = np.interp(altitudes, DRCT_heights_PM, DRCT_values_PM).tolist()
        allSamplesRadPM['DRCT'] = DRCT_samples_PM;
        
        SKNT_heights_PM.resize(len(SKNT_samples_PM))
        SKNT_values_PM.resize(len(SKNT_samples_PM))
        allValuesRadPM['SKNT'] = np.interp(altitudes, SKNT_heights_PM, SKNT_values_PM).tolist()
        allSamplesRadPM['SKNT'] = SKNT_samples_PM;
        
        # Critical humidity function
        alpha = 1.0
        beta = np.sqrt(3)
        sigma = np.array(allValuesRadPM['PRES'])/allValuesRadPM['PRES'][0]
        chum = 1 - alpha*sigma*(1 - sigma)*(1+beta*(sigma - 0.5));
        allValuesRadPM['clouds'] = np.int_(np.array(allValuesRadPM['RELH']) > chum * 100).tolist()
        
        allValuesRadPM['HGHT'] = altitudes.tolist()
        args['allValuesRadPM'] = allValuesRadPM
        args['allSamplesRadPM'] = allSamplesRadPM
    
    args['itemsRad'] = {'Pressure (hPa)': 'PRES', 'Temperature (deg. C)': 'TEMP', 'Dew point (deg. C)': 'DWPT', 'Rel. humidity (%)': 'RELH', 'Wind direction (deg.)': 'DRCT', 'Wind speed (knot)': 'SKNT'}
    args['googleKey'] = settings.GOOGLE_MAPS_API_KEY
    
    return render(request, 'visualization/index.html', args)

