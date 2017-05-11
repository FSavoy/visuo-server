#!/usr/bin/env python

"""
Sample script running on a single board computer inside a sky imager. It uses the gphoto2 library to control the camera, capture images and send them to the visuo server.
"""

import datetime
import subprocess
import zc.lockfile

url = "[INSERT BASE URL HERE]/api/skypicture/"
authHeader = "Authorization: Token [INSERT SKY IMAGER USER TOKEN HERE]"

dt = datetime.datetime.now()
print '--------------------------'
print 'Capture image'
print dt
lock = zc.lockfile.LockFile('/home/odroid/Scripts/lock')

attemptsLeft = 10
while attemptsLeft > 0:
    try:
        out = subprocess.check_output(['gphoto2', '--capture-image-and-download'])
        attemptsLeft = 0
    except:
        attemptsLeft = attemptsLeft - 1
        import time
        time.sleep(0.5)
        print 'Failed: ' + str(attemptsLeft) + ' attempts left'

files = []
for outline in out.split("\n"):
        if "Saving file as" in outline:
                files.append(outline.split(' ')[3])

print 'Number of files: ' + str(len(files))
if len(files) != 1:
    print 'Number of files not equal to 1'
    print out

filename_tmp = files[0]

lock.close()
print 'Unlocked the lock'

import sys
import pycurl
import os.path
import shutil
import os
import time

# Uploading to the server
delay = 1
max_delay = 172800
sucess = False

if not os.path.isfile(filename_tmp):
    print 'File not found: ' + filename_tmp
    raise IOError("File not found")

try:
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, [authHeader])
    c.setopt(pycurl.POST, 1)
    data = [('image', (c.FORM_FILE, filename_tmp))]
    c.setopt(pycurl.HTTPPOST, data)
    c.perform()
    c.close()
    os.remove(filename_tmp)
    sucess = True
except:
    print "Transfer failed"
    os.remove(filename_tmp)