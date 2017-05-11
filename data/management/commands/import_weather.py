from django.core.management.base import BaseCommand
import csv
from data.models import WeatherMeasurement, MeasuringDevice
import datetime

class Command(BaseCommand):
    help = 'Import weather data from a Vantage Pro 2 weather station generated archive file.'
    
    def add_arguments(self, parser):
    
        parser.add_argument(
            '--file',
            action = 'store',
            dest = 'file',
            default = False,
            help = 'File to read',
        )
        
        parser.add_argument(
            '--device',
            action = 'store',
            dest = 'device',
            default = False,
            help = 'Name of the weather station as stored in the database',
        )
        
        
    def handle(self, *args, **options):
        # now do the things that you want with your models here
        try:
            f = open(options['file'])
        except:
            print ('Missing input file or unable to open')
            return
            
        try:
            station = MeasuringDevice.objects.get(name = options['name'])
        except:
            print 'Missing or wrong device name'
            return
        
        with f as tsv:
            for line in csv.reader(tsv, delimiter="\t"): #You can also use delimiter="\t" rather than giving a dialect.
                
                if line[0] == '' or line[0] == 'Date':
                    continue
                
                meas = WeatherMeasurement()
                
                meas.device = station
                print 'Device: ' + str(meas.device)
                
                meas.date = datetime.datetime.strptime(line[0], "%m/%d/%y").date()
                print 'Date: ' + str(meas.date)
                
                meas.time = datetime.datetime.strptime(line[1].replace('a', 'AM').replace('p', 'PM'), "%I:%M %p").time()
                print 'Time: ' + str(meas.time)
                
                meas.temperature = self.floatToString(line[2])
                print 'Temperature: ' + str(meas.temperature)
                
                meas.humidity = self.floatToString(line[5])
                print 'Humidity: ' + str(meas.humidity)
                
                meas.dew_point = self.floatToString(line[6])
                print 'Dew point: ' + str(meas.dew_point)
                
                meas.wind_speed = self.floatToString(line[7])
                print 'Wind speed: ' + str(meas.wind_speed)
                
                meas.wind_direction = self.directionToStringAngle(line[8])
                print 'Wind direction: ' + str(meas.wind_direction)
                
                meas.pressure = self.floatToString(line[14])
                print 'Pressure: ' + str(meas.pressure)
                
                meas.rainfall_rate = self.floatToStringTimes60(line[15])
                print 'Rainfall rate: ' + str(meas.rainfall_rate)
                
                meas.solar_radiation = None
                print 'Solar radiation: ' + str(meas.solar_radiation)
                
                meas.uv_index = None
                print 'UV index: ' + str(meas.uv_index)
                
                print '-------------'
                meas.save()
                
    def floatToString(self, inputStr):
        try:
            value = float(inputStr)
        except ValueError:
            value = None
        return value
    
    def floatToStringTimes60(self, inputStr):
        try:
            value = 60*float(inputStr)
        except ValueError:
            value = None
        return value
    
    def directionToStringAngle(self, inputStr):
        if inputStr == 'N':
            return '0'
        elif inputStr == 'NNE':
            return '22.5'
        elif inputStr == 'NE':
            return '45'
        elif inputStr == 'ENE':
            return '67.5'
        elif inputStr == 'E':
            return '90'
        elif inputStr == 'ESE':
            return '112.5'
        elif inputStr == 'SE':
            return '135'
        elif inputStr == 'SSE':
            return '157.5'
        elif inputStr == 'S':
            return '180'
        elif inputStr == 'SSW':
            return '202.5'
        elif inputStr == 'SW':
            return '225'
        elif inputStr == 'WSW':
            return '247.5'
        elif inputStr == 'W':
            return '270'
        elif inputStr == 'WNW':
            return '292.5'
        elif inputStr == 'NW':
            return '315'
        elif inputStr == 'NNW':
            return '337.5'
        else:
            return None

    