#
# Ricardo de Azambuja
# http://ricardodeazambuja.com
#
# Based (copied) from my friend Massimiliano:
# https://github.com/mpatacchiola/pyERA/blob/master/examples/ex_nao_head_imitation/ex_nao_head_imitation.py
#

import numpy
import matplotlib.pyplot as plt
import time

from naoqi import ALProxy

NAO_IP = "192.168.1.100"
NAO_PORT = 9559


#Getting the nao proxies
ALVideoProxy = ALProxy("ALVideoDevice", NAO_IP, int(NAO_PORT))

try:
    # Subscribe to the proxies services
    try:
        #"Test_Video", CameraIndex=1, Resolution=1, ColorSpace=0, Fps=5
        #CameraIndex= 0(Top), 1(Bottom)
        #Resolution= 0(160*120), 1(320*240), VGA=2(640*480), 3(1280*960)
        #ColorSpace= AL::kYuvColorSpace (index=0, channels=1), AL::kYUV422ColorSpace (index=9,channels=3),
        #AL::kRGBColorSpace RGB (index=11, channels=3), AL::kBGRColorSpace BGR (to use in OpenCV) (index=13, channels=3)
        #Fps= OV7670 VGA camera can only run at 30, 15, 10 and 5fps. The MT9M114 HD camera run from 1 to 30fps.
        #Settings for resolution 1 (320x240)
        resolution_type = 1
        fps=15
        cam_w = 320
        cam_h = 240
        #Settigns for resolution 2 (320x240)
        #resolution_type = 2
        #fps = 15
        #cam_w = 640
        #cam_h = 480
        camera_name_id = ALVideoProxy.subscribeCamera("StreamingVideo", 0, resolution_type, 13, fps)
    except BaseException, err:
        print str(err)

    plt.ion()

    while True:
        # In this state it is captured a stream of images from
        # the NAO camera and it is convertend in a Numpy matrix
        # The Numpy matrix cam be analysed as an image from OpenCV
        #Get Images from camera
        naoqi_img = ALVideoProxy.getImageRemote(camera_name_id)
        if(naoqi_img != None):
            img = (
                   numpy.reshape(
                      numpy.frombuffer(naoqi_img[6], dtype='%iuint8' % naoqi_img[2]),
                      (naoqi_img[1], naoqi_img[0], naoqi_img[2])
                              )
                   )
        else:
           img = numpy.zeros((cam_h, cam_w))
        img = numpy.copy(img)

        #Show the image and record the video
        plt.imshow(img[:,:,::-1])

        plt.pause(0.05)

finally:
    ALVideoProxy.unsubscribe(camera_name_id)
