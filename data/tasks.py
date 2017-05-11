from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
import numpy as np
import os
from django.conf import settings
from PIL import Image
from data.models import SkyPicture
from alligator import Gator
import scipy.misc

# The gator instance to run the tasks outside the web server scope
gator = Gator(settings.ALLIGATOR_CONN)


def computeProjection(skyPictureInstance_id):
    """
    Computes the projection of the image to be displayed on the map. Does a dummy crop and adds a transparency layer. To be modified according to fisheye calibration.
    """
    
    skyPictureInstance = SkyPicture.objects.get(id = skyPictureInstance_id)
    
    # Check if it has not already been computed for this instance
    if not skyPictureInstance.undistorted or skyPictureInstance.undistorted == 'undistorted/TODO.png':
        img = np.asarray(Image.open(os.path.join(settings.BASE_DIR, skyPictureInstance.image.url[1:])))
        
        if img.shape[0] > img.shape[1]:
            img = np.rot90(img)
            
        img = np.flip(img,0)
        
        img = img[:, (np.shape(img)[1]/2 - np.shape(img)[0]/2):(np.shape(img)[1]/2 + np.shape(img)[0]/2), :]
        img = transparency(img)
        img_pil_response = Image.fromarray(img, "RGBA")
        
        # fetch image into memory
        temp_handle = StringIO()
        img_pil_response.save(temp_handle, 'PNG', option='optimize')
        temp_handle.seek(0)
        
        filename = skyPictureInstance.date.strftime("%Y-%m-%d-") + skyPictureInstance.time.strftime("%H-%M-%S.png")
        suf = SimpleUploadedFile(filename, temp_handle.read(), content_type='image/png')
        skyPictureInstance.undistorted.save(filename, suf, False)
        skyPictureInstance.save()


def transparency(img):
    """
    Adds transparency according to a pre-computed mask of the central circle.
    """
    
    black_mask_undistorted_file = open(os.path.join(settings.BASE_DIR, 'static', 'mask_undistorted.npy'), 'r')
    black_mask_undistorted = np.load(black_mask_undistorted_file)
    alpha = 200 * black_mask_undistorted
    img = scipy.misc.imresize(img, (np.shape(alpha)[0], np.shape(alpha)[1]))

    result = np.empty([img.shape[0], img.shape[1], 4], dtype=np.uint8)
    result[:,:,0] = img[:,:,0]
    result[:,:,1] = img[:,:,1]
    result[:,:,2] = img[:,:,2]
    result[:,:,3] = alpha

    return result


