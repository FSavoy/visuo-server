from django.core.management.base import BaseCommand
from data.models import MeasuringDevice, RadiosondeMeasurement
from django.conf import settings
import urllib2
import urllib
import datetime


class Command(BaseCommand):
    help = 'Download radiosonde data form the University of Wyoming website. Takes an optional period of time to download'
    
    def add_arguments(self, parser):
    
        parser.add_argument(
            '--start-date',
            action = 'store',
            dest = 'start-date',
            default = False,
            help = 'Starting date for downloading data (YYYY-mm-dd)',
        )
        
        parser.add_argument(
            '--end-date',
            action = 'store',
            dest = 'end-date',
            default = False,
            help = 'Starting date for downloading data (YYYY-mm-dd)',
        )

    
    def handle(self, *args, **options):
        
        device = MeasuringDevice.objects.get(type = 'R')
        
        # Period of data
        if options['start-date'] and options['end-date']:
            
            stop = datetime.datetime.strptime(options['end-date'], '%Y-%m-%d')
            start = datetime.datetime.strptime(options['start-date'], '%Y-%m-%d')
            delta = stop - start
            
            daterange = []
            for i in range(delta.days + 1):
                daterange.append(stop - datetime.timedelta(days=i))
                daterange.append(stop - datetime.timedelta(days=i) + datetime.timedelta(hours=12))
                
            for date in daterange:
                data = self.getRadiosondeData(date)
                self.storeData(data, device)
                
        elif options['start-date'] or options['end-date']:
            print "None or both start or end date should be given"
        else:
            data = self.getRadiosondeData()
            self.storeData(data, device)
            
            
    def storeData(self, data, device):
        """
        Stores the data in the django database
        """
        
        for line in data:
            r = RadiosondeMeasurement()
            r.time = line['time']
            r.date = datetime.datetime.strptime(line['date'], "%Y-%m-%d")
            r.pressure = float(line['PRES'])
            r.height = float(line['HGHT'])
            r.temperature = float(line['TEMP'])
            r.dew_point = float(line['DWPT'])
            r.rel_humidity = float(line['RELH'])
            r.wind_direction = float(line['DRCT'])
            r.wind_speed = float(line['SKNT'])
            r.device = device
            
            r.save()
            print 'Saved ' + str(r)    
    
        
    def getRadiosondeData(self, date = datetime.datetime.now()):
        """
        Downloads the radiosonde data from the University of Wyoming website
        """
        
        data = {}
        data['region'] = 'naconf'
        data['TYPE'] = 'TEXT:LIST'
        data['YEAR'] = date.strftime('%Y')
        data['MONTH'] = date.strftime('%m')
        if date.hour < 12:
            data['FROM'] = date.strftime('%d') + '00'
            data['TO'] = date.strftime('%d') + '00'
        else:
            data['FROM'] = date.strftime('%d') + '12'
            data['TO'] = date.strftime('%d') + '12'
        data['STNM'] = settings.RADIOSONDE_ID
        
        url = 'http://weather.uwyo.edu/cgi-bin/sounding'
        url_full = url + '?' + urllib.urlencode(data)
        print url_full
        
        f = urllib2.urlopen(url_full)
        content = f.readlines()
        f.close()
        try:
            content.remove('-----------------------------------------------------------------------------\n')
            startIdx =  content.index('-----------------------------------------------------------------------------\n')
            endIdx = content.index('</PRE><H3>Station information and sounding indices</H3><PRE>\n')
            content = content[startIdx+1:endIdx]
            
            def readval(string):
                try:
                    val = float(string)
                except ValueError:
                    val = float('NaN')
                return val
            
            data = []
            for line in content:
                dataitem = {}
                dataitem['date'] = date.strftime('%Y-%m-%d')
                dataitem['time'] = date.strftime('%p').upper()
                dataitem['PRES'] = readval(line[0:7])
                dataitem['HGHT'] = readval(line[7:14])
                dataitem['TEMP'] = readval(line[14:21])
                dataitem['DWPT'] = readval(line[21:28])
                dataitem['RELH'] = readval(line[28:35])
                dataitem['MIXR'] = readval(line[35:42])
                dataitem['DRCT'] = readval(line[42:49])
                dataitem['SKNT'] = readval(line[49:56]) * 0.514444444 # conversion knot - m/s
                dataitem['THTA'] = readval(line[56:63])
                dataitem['THTE'] = readval(line[63:70])
                dataitem['THTV'] = readval(line[70:77])
                data.append(dataitem)
        
            return data
        except:
            return []
      
 