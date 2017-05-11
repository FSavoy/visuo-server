from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.http import HttpResponse
import cStringIO
from data.models import RadiosondeMeasurement, WeatherMeasurement, MeasuringDevice
from forms import WeatherMeasurementForm, RadiosondeMeasurementForm
import numpy as np
import scipy.io
import xlsxwriter

@login_required
def index(request):
    """
    Main view for the page, handles the forms.
    """
    
    # Fetch POST data and redirects to the corresponding view if a button has been clicked.
    if request.POST:
        form_values = request.POST
        if 'matlab-weather' in request.POST:
            form_weather = WeatherMeasurementForm(form_values)
            request.session['POSTweather'] = form_values
            if form_weather.is_valid():
                return matlab_weather(request, form_weather)
            
        if 'matlab-radiosonde' in request.POST:
            form_radiosonde = RadiosondeMeasurementForm(form_values)
            request.session['POSTradiosonde'] = form_values
            if form_radiosonde.is_valid():
                return matlab_radiosonde(request, form_radiosonde)
            
        if 'excel-weather' in request.POST:
            form_weather = WeatherMeasurementForm(form_values)
            request.session['POSTweather'] = form_values
            if form_weather.is_valid():
                return excel_weather(request, form_weather)
            
        if 'excel-radiosonde' in request.POST:
            form_radiosonde = RadiosondeMeasurementForm(form_values)
            request.session['POSTradiosonde'] = form_values
            if form_radiosonde.is_valid():
                return excel_radiosonde(request, form_radiosonde)
            
    # Loads or initializes the weather data form
    if 'POSTweather' in request.session:
        form_weather = WeatherMeasurementForm(request.session['POSTweather'])
    else:
        form_weather = WeatherMeasurementForm()
    
    # Loads or initializes the radionsonde data form
    if 'POSTradiosonde' in request.session:
        form_radiosonde = RadiosondeMeasurementForm(request.session['POSTradiosonde'])
    else:
        form_radiosonde = RadiosondeMeasurementForm()
        

    args = {}
    args.update(csrf((request)))
    args['form_weather'] = form_weather
    args['form_radiosonde'] = form_radiosonde
    
    # Indicates if the radionsonde data form should be displayed
    if MeasuringDevice.objects.filter(type = 'R').exists() & RadiosondeMeasurement.objects.exists():
        args['radiosonde_data_available'] = True
    else:
        args['radiosonde_data_available'] = False
    
    # Indicates if the weather data form should be displayed
    if MeasuringDevice.objects.filter(type = 'S').exists() & WeatherMeasurement.objects.exists():
        args['weather_data_available'] = True
    else:
        args['weather_data_available'] = False
        
    args['title'] = 'Data downloads'
    
    return render(request, 'downloads/index.html', args)


@login_required
def matlab_radiosonde(request, form):
    """
    Reads the radiosonde form and converts the data into a matlab file
    """
    
    start = form.cleaned_data['start_date_radiosonde']
    end = form.cleaned_data['end_date_radiosonde']
    time = form.cleaned_data['time_radiosonde']
    fields = form.cleaned_data['fields_radiosonde']
    
    query = RadiosondeMeasurement.objects.filter(date__gte = start, date__lte = end, time__in = time).values()
    radiosonde = dict()
    for elem in query:
        date = elem['date'].strftime('y%Ym%md%d')
        if date not in radiosonde:
            radiosonde[date] = dict()
        if elem['time'] not in radiosonde[date]:
            radiosonde[date][str(elem['time'])] = []
        radiosonde[date][elem['time']].append(elem)
        
    dtfields = []
    for f in fields:
        dtfields.append((str(f), 'f8'))
    for d in radiosonde:
        for t in radiosonde[d]:
            nbElems = len(radiosonde[d][t])
            res = np.zeros((nbElems,), dtype=dtfields)
            idx = 0
            for elem in radiosonde[d][t]:
                for f in fields:
                    res[idx][str(f)] = elem[str(f)]
                idx = idx + 1
            radiosonde[d][t] = res
            
    for d in radiosonde:
        if 'AM' in radiosonde[d] and 'PM' in radiosonde[d]:
            dtAMPM = [('AM', np.object), ('PM', np.object)]
            res = np.zeros((1,), dtype=dtAMPM)
            res[0]['AM'] = radiosonde[d]['AM']
            res[0]['PM'] = radiosonde[d]['PM']
            radiosonde[d] = res
        elif 'AM' in radiosonde[d]:
            dtAM = [('AM', np.object)]
            res = np.zeros((1,), dtype=dtAM)
            res[0]['AM'] = radiosonde[d]['AM']
            radiosonde[d] = res
        elif 'PM' in radiosonde[d]:
            dtAM = [('PM', np.object)]
            res = np.zeros((1,), dtype=dtAM)
            res[0]['PM'] = radiosonde[d]['PM']
            radiosonde[d] = res
            
    dtdays = []
    for d in radiosonde:
        dtdays.append((d, np.object))
    dtdays.sort()
    result = np.zeros((1,), dtype=dtdays)
    for d in radiosonde:
        result[0][d] = radiosonde[d]
    
    fobj = cStringIO.StringIO()
    response = HttpResponse(content_type='application/matlab-mat')
    response['Content-Disposition'] = 'attachment; filename=radiosonde.mat'
    scipy.io.savemat(fobj, {'radiosonde': result}, oned_as='column')
    response.write(fobj.getvalue())
    
    return response


@login_required
def matlab_weather(request, form):
    """
    Reads the weather form and converts the data into a matlab file
    """
    
    start_date = form.cleaned_data['start_date_weather']
    end_date = form.cleaned_data['end_date_weather']
    start_time = form.cleaned_data['start_time_weather']
    end_time = form.cleaned_data['end_time_weather']
    measuring_device = MeasuringDevice.objects.get(id = form.cleaned_data['measuring_device_weather'])
    fields = form.cleaned_data['fields_weather']
    
    query = WeatherMeasurement.objects.filter(date__gte = start_date, date__lte = end_date, time__gte = start_time, time__lte = end_time, device = measuring_device).values()
    weather = dict()
    
    for elem in query:
        date = elem['date'].strftime('y%Ym%md%d')
        time = elem['time'].strftime('h%Hm%Ms%S')
        if date not in weather:
            weather[date] = dict()
        if elem['time'] not in weather[date]:
            weather[date][time] = []
        weather[date][time].append(elem)
        
    dtfields = []
    for f in fields:
        dtfields.append((str(f), 'f8'))
    for d in weather:
        for t in weather[d]:
            nbElems = len(weather[d][t])
            res = np.zeros((nbElems,), dtype=dtfields)
            idx = 0
            for elem in weather[d][t]:
                for f in fields:
                    res[idx][str(f)] = elem[str(f)]
                idx = idx + 1
            weather[d][t] = res
            
    for d in weather:
        dttime = []
        for t in weather[d]:
            dttime.append((t, np.object))
        dttime.sort()
        resultTime = np.zeros((1,), dtype=dttime)
        for t in weather[d]:
            resultTime[0][t] = weather[d][t]
        weather[d] = resultTime
            
    dtdays = []
    for d in weather:
        dtdays.append((d, np.object))
    dtdays.sort()
    result = np.zeros((1,), dtype=dtdays)
    for d in weather:
        result[0][d] = weather[d]
    
    fobj = cStringIO.StringIO()
    response = HttpResponse(content_type='application/matlab-mat')
    response['Content-Disposition'] = 'attachment; filename=weather.mat'
    scipy.io.savemat(fobj, {'weather': result}, oned_as='column')
    response.write(fobj.getvalue())
    
    return response


@login_required
def excel_radiosonde(request, form):
    """
    Reads the radiosonde form and converts the data into a excel file
    """
    
    start = form.cleaned_data['start_date_radiosonde']
    end = form.cleaned_data['end_date_radiosonde']
    time = form.cleaned_data['time_radiosonde']
    fields = form.cleaned_data['fields_radiosonde']
    
    query = RadiosondeMeasurement.objects.filter(date__gte = start, date__lte = end, time__in = time).order_by('date').values()
    
    fobj = cStringIO.StringIO()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=radiosonde.xlsx'
    
    workbook = xlsxwriter.Workbook(fobj)
    worksheet = workbook.add_worksheet()
    
    # Adjust the column width.
    worksheet.set_column(0, 0, 10)
    # Adjust the column width.
    worksheet.set_column(1, 1, 5)

    
    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'dd mm yyyy'})
    
    worksheet.write(0,0, 'Date', bold)
    worksheet.write(0,1, 'Time', bold)
    
    col = 2
    if 'pressure' in fields:
        worksheet.write(0, col, 'Atmospheric pressure (hPa)', bold)
        col = col + 1
    if 'height' in fields:
        worksheet.write(0, col, 'Geopotential height (m)', bold)
        col = col + 1
    if 'temperature' in fields:
        worksheet.write(0, col, 'Temperature (C)', bold)
        col = col + 1
    if 'dew_point' in fields:
        worksheet.write(0, col, 'Dewpoint temperature (C)', bold)
        col = col + 1
    if 'rel_humidity' in fields:
        worksheet.write(0, col, 'Relative humidity (%)', bold)
        col = col + 1
    if 'wind_direction' in fields:
        worksheet.write(0, col, 'Wind direction (deg)', bold)
        col = col + 1
    if 'wind_speed' in fields:
        worksheet.write(0, col, 'Wind speed (m/s)', bold)
        col = col + 1

    for row, elem in enumerate(query, start = 1):
        worksheet.write_datetime(row, 0, elem['date'], date_format)
        worksheet.write_string(row, 1, elem['time'])
        
        for col, f in enumerate(fields, start = 2):
            worksheet.write(row, col, elem[f])
        col = 2
    
    workbook.close()
    response.write(fobj.getvalue())
    
    return response

    
@login_required
def excel_weather(request, form):
    """
    Reads the weather form and converts the data into a excel file
    """
    
    start_date = form.cleaned_data['start_date_weather']
    end_date = form.cleaned_data['end_date_weather']
    start_time = form.cleaned_data['start_time_weather']
    end_time = form.cleaned_data['end_time_weather']
    measuring_device = MeasuringDevice.objects.get(id = form.cleaned_data['measuring_device_weather'])
    fields = form.cleaned_data['fields_weather']
    
    query = WeatherMeasurement.objects.filter(date__gte = start_date, date__lte = end_date, time__gte = start_time, time__lte = end_time, device = measuring_device).values()
    
    fobj = cStringIO.StringIO()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=radiosonde.xlsx'
    
    workbook = xlsxwriter.Workbook(fobj)
    worksheet = workbook.add_worksheet()
    
    # Adjust the column widths.
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 1, 5)
    
    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    time_format = workbook.add_format({'num_format': 'hh:mm'})
    
    worksheet.write(0,0, 'Date', bold)
    worksheet.write(0,1, 'Time', bold)
    
    texts = {'temperature':'Temperature (C)',
             'humidity':'Humidity (%)',
             'dew_point':'Dew point (C)',
             'wind_speed':'Wind speed (m/s)',
             'wind_direction':'Wind direction (deg)',
             'pressure':'Pressure (hPa)',
             'rainfall_rate':'Rainfall rate (mm/hr)',
             'solar_radiation':'Solar radiation (W/m2)',
             'uv_index':'UV Index'}
    
    for col, f in enumerate(fields, start = 2):
            worksheet.write(0, col, texts[f])

    for row, elem in enumerate(query, start = 1):
        worksheet.write_datetime(row, 0, elem['date'], date_format)
        worksheet.write_datetime(row, 1, elem['time'], time_format)
        
        for col, f in enumerate(fields, start = 2):
            worksheet.write(row, col, elem[f])
    
    workbook.close()
    response.write(fobj.getvalue())
    
    return response

