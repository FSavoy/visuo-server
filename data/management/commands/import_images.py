from django.core.management.base import BaseCommand
from django.core.files import File
import os
import exifread
from data.models import SkyPicture, MeasuringDevice
import datetime
from fractions import Fraction
from data.tasks import gator, computeProjection


class Command(BaseCommand):
    help = 'Import sky images stored in a user specified folder'
    
    def add_arguments(self, parser):
    
        parser.add_argument(
            '--folder',
            action = 'store',
            dest = 'folder',
            default = False,
            help = 'Folder to read',
        )
        
        parser.add_argument(
            '--device',
            action = 'store',
            dest = 'device',
            default = False,
            help = 'Name of the sky imager as stored in the database',
        )
    
    
    def handle(self, *args, **options):
        
        print options
        
        try:
            directory = options['folder']
            files_in_dir = os.listdir(directory)
        except:
            print ('Missing input file or unable to open')
            return
        
        try:
            print options['device']
            device = MeasuringDevice.objects.get(name = options['device'])
        except:
            print 'Missing or wrong device name'
            return

        for file_in_dir in files_in_dir:
            
            if os.path.isdir(os.path.join(directory, file_in_dir)):
                continue
            
            if not file_in_dir.endswith(('JPG', 'jpg', 'jpeg')):
                continue
            
            print 'Current file: ' + file_in_dir
            
            # Create a new sky imager object, reading values from EXIF metadata
            img = SkyPicture()
            img.device = device
            
            try:
                f = open(os.path.join(directory, file_in_dir), 'r')
                tags = exifread.process_file(f)
            except:
                continue
            
            if not 'EXIF ExposureTime' in tags or not 'EXIF FNumber' in tags or not 'EXIF ISOSpeedRatings' in tags or not 'EXIF DateTimeOriginal' in tags:
                continue
            
            img.exposure_time = str(float(Fraction(str(tags['EXIF ExposureTime']))))
            print 'Exposure time: ' + str(img.exposure_time)
            
            img.aperture_value =  str(float(Fraction(str(tags['EXIF FNumber']))))
            print 'Aperture value: ' + str(img.aperture_value)
            
            img.ISO_speed =  int(str(tags['EXIF ISOSpeedRatings']))
            print 'ISO speed: ' + str(img.ISO_speed)
            
            dt = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
            img.date = dt.date()
            print 'Date: ' + str(img.date)
            img.time = dt.time()
            print 'Time: ' + str(img.time)
            
            img.undistorted = "undistorted/TODO.png"
            
            if SkyPicture.objects.filter(device = img.device).filter(date = img.date).filter(time = img.time).count() > 0:
                print 'Image already in the database'
                continue
            
            filename = dt.strftime("%Y-%m-%d-%H-%M-%S-") + img.device.username.username + ".jpg"
            print filename
            
            img.image.save(filename, File(f), True)
            
            img.save()
            gator.task(computeProjection, img.id)
            print ''


