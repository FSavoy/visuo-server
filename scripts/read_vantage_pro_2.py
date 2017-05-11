import time
import json
import datetime
import pycurl
from ctypes import *
import math
import datetime as dt
from datetime import timedelta
import os.path

"""
Sample script reading a Davis Vantage Pro weather station data file and sending the latest weather measurements to the server.
Based on: http://www.wviewweather.com/vpro-docs/binary_file_format-5.4.txt
"""

# The folder on the local PC in which the weahter station data files are stored
folder = 'C:\\WeatherLink\\WS11\\'

# The url of the visuo server
url = "[INSERT BASE URL HERE]/api/weathermeasurement/"

# The authentication header of the weather station username on the server
authHeader = "Authorization: Token [INSERT TOKEN HERE]"

class WeatherDataRecord(Structure):
    _fields_ = [('dataType', c_ubyte),
                ('archiveInterval', c_ubyte),
                ('iconFlags', c_ubyte),
                ('moreFlags', c_ubyte),
                ('packedTime', c_short),
                ('outsideTemp', c_short),
                ('hiOutsideTemp', c_short),
                ('lowOutsideTemp', c_short),
                ('insideTemp', c_short),
                ('barometer', c_short),
                ('outsideHum', c_short),
                ('insideHum', c_short),
                ('rain', c_ushort),
                ('hiRainRate', c_short),
                ('windSpeed', c_short),
                ('hiWindSpeed', c_short),
                ('windDirection', c_ubyte),
                ('hiWindDirection', c_ubyte),
                ('numWindSamples', c_short),
                ('solarRad', c_short),
                ('hisolarRad', c_short),
                ('UV', c_ubyte),
                ('hiUV', c_ubyte),
                ('leafTemp0', c_ubyte),
                ('leafTemp1', c_ubyte),
                ('leafTemp2', c_ubyte),
                ('leafTemp3', c_ubyte),
                ('extraRad', c_short),
                ('newSensors0', c_short),
                ('newSensors1', c_short),
                ('newSensors2', c_short),
                ('newSensors3', c_short),
                ('newSensors4', c_short),
                ('newSensors5', c_short),
                ('forecast', c_ubyte),
                ('ET', c_ubyte),
                ('soilTemp0', c_ubyte),
                ('soilTemp1', c_ubyte),
                ('soilTemp2', c_ubyte),
                ('soilTemp3', c_ubyte),
                ('soilTemp4', c_ubyte),
                ('soilTemp5', c_ubyte),
                ('soilMoisture0', c_ubyte),
                ('soilMoisture1', c_ubyte),
                ('soilMoisture2', c_ubyte),
                ('soilMoisture3', c_ubyte),
                ('soilMoisture4', c_ubyte),
                ('soilMoisture5', c_ubyte),
                ('leafWetness0', c_ubyte),
                ('leafWetness1', c_ubyte),
                ('leafWetness2', c_ubyte),
                ('leafWetness3', c_ubyte),
                ('extraTemp0', c_ubyte),
                ('extraTemp1', c_ubyte),
                ('extraTemp2', c_ubyte),
                ('extraTemp3', c_ubyte),
                ('extraTemp4', c_ubyte),
                ('extraTemp5', c_ubyte),
                ('extraTemp6', c_ubyte),
                ('extraHum0', c_ubyte),
                ('extraHum1', c_ubyte),
                ('extraHum2', c_ubyte),
                ('extraHum3', c_ubyte),
                ('extraHum4', c_ubyte),
                ('extraHum5', c_ubyte),
                ('extraHum6', c_ubyte)]
    
def readFile(filename):
    with open(filename, 'rb') as file:
        measure = WeatherDataRecord()
        file.seek(-88, 2)
        file.readinto(measure)
        file.close()
        
    if measure.dataType == 1:
        time = measure.packedTime
        mins = time % 60
        hours = (time - mins)/60
        time = dt.time(hours, mins, 0)
        temperature = round((float(measure.outsideTemp) / 10 - 32) * 5/9, 1)
        humidity = float(measure.outsideHum) / 10
        if humidity == -3276.8:
            humidity = "None"
        pressure = round(float(measure.barometer) / 1000 * 33.864,1)
        try:
            v = humidity*0.01*6.112*math.exp((17.62*temperature)/(temperature+243.12))
            num = 243.12*math.log(v)-440.1
            den = 19.43 - math.log(v)
            dew_point = round(num/den,1)
        except Exception,e:
            dew_point = "None"
        wind_speed = round(float(measure.windSpeed) / 10 * 0.44704, 1)
        wind_direction = float(measure.windDirection) * 22.5
        if wind_direction == 5737.5:
            wind_direction = "None"
        rain = measure.rain
        rain_amount = float(rain) % 4096
        rain_type = (rain - rain_amount)/4096
        if rain_type == 0:
            rain = rain_amount * 0.1 * 25.4
        elif rain_type == 1:
            rain = rain_amount * 0.01 * 25.4
        elif rain_type == 2:
            rain = rain_amount * 0.2
        elif rain_type == 3:
            rain = rain_amount
        else:
            rain = rain_amount * 0.1
        
        solar_radiation = measure.solarRad
        if solar_radiation == -32768:
            solar_radiation = "None"
        uv = float(measure.UV) / 10
        if uv == 25.5:
            uv = "None"
        
        now = dt.datetime.now()
        date = now.date()
        # Because of misalignements in the clocks, we can be on two different days
        elevenPM = dt.time(23,0,0)
        oneAM = dt.time(1,0,0)
        if now.time() < oneAM and time > elevenPM:
            date = date - timedelta(days=1)
        elif now.time() > elevenPM and time < oneAM:
            date = date + timedelta(days=1)
        
        data = {}
        data['date'] = str(date)
        data['time'] = str(time)
        data['temperature'] = str(temperature)
        data['humidity'] = str(humidity)
        data['dew_point'] = str(dew_point)
        data['wind_speed'] = str(wind_speed)
        data['wind_direction'] = str(wind_direction)
        data['pressure'] = str(pressure)
        data['rainfall_rate'] = str(60*rain)
        data['solar_radiation'] = str(solar_radiation)
        data['solar_energy'] = '0.0'
        data['uv_index'] = str(uv)
        data['uv_dose'] = '0.0'
        return data
    else:
        raise Exception('Not a weather information')


lastDatetime = datetime.datetime.fromtimestamp(0)

while 1:
    try:
        filename = folder + dt.datetime.now().strftime('%Y-%m.wlk')
        if not os.path.isfile(filename):
            filename = folder + (dt.datetime.now() - timedelta(months=1)).strftime('%Y-%m.wlk')
                        
        data = readFile(filename)
        dataJSON = json.dumps(data)
                            
        thisDate = data['date']
        thisTime = data['time']
        thisDatetime = datetime.datetime.strptime(thisDate + " " + thisTime, '%Y-%m-%d %H:%M:%S')
        if thisDatetime > lastDatetime:
            try:
                print 'Updating:'
                c = pycurl.Curl()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.HTTPHEADER, [authHeader, 'Content-Type: application/json'])
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.POSTFIELDS, dataJSON)
                c.setopt(c.SSL_VERIFYPEER, 0)
                c.perform()
                c.close()
                lastDatetime = thisDatetime
                print ''
            except Exception,e:
                print 'Exception 1: ' + str(e)
        
    except Exception, e:
        print 'Exception 2:' + str(e)
    
    time.sleep(15)