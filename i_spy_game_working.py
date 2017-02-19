#
# Ricardo de Azambuja
# http://ricardodeazambuja.com
#
# Based (copied) from my friend Massimiliano:
# https://github.com/mpatacchiola/pyERA/blob/master/examples/ex_nao_head_imitation/ex_nao_head_imitation.py
#

# http://doc.aldebaran.com/1-14/naoqi/index.html

import numpy
import matplotlib.pyplot as plt
import time

from multiprocessing import Process

import requests

import StringIO
from PIL import Image

from naoqi import ALProxy

import almath

import mtranslate

from speech_recognition import *

SpeachRec = myBroker = None

def foo(NAO_IP = "192.168.1.100", NAO_PORT = 9559):
    global SpeachRec, myBroker

    # Variables
    _url_vision_analise = 'https://westus.api.cognitive.microsoft.com/vision/v1.0/analyze'
    _url_vision_describe = 'https://westus.api.cognitive.microsoft.com/vision/v1.0/describe'
    _url_linguistic = 'https://westus.api.cognitive.microsoft.com/linguistics/v1.0/analyze'

    _maxNumRetries = 10


    _key_vision = '9576f4ea8f2f440594f31865a844817f' #Here you have to paste your primary key (mine is invalid now...)
    _key_emotion = '77d1221c40be49198fd278132ea4fdca' #Here you have to paste your primary key (mine is invalid now...)
    _key_ling = 'a72eeef4a77c403095b9f025dc6f5a80'


    def to_stream(img, format='PNG'):
        imgdata = StringIO.StringIO() # Behaves just like an openned file
        pil = Image.fromarray(numpy.copy(img))
        if format=='PNG':
            pil.save(imgdata, format='PNG', quality=0.3, optimize=True)
        elif format=='JPEG':
            pil.save(imgdata, format='JPEG', quality=50, optimize=True)
        imgdata.seek(0)
        return imgdata.getvalue()


    def processRequest( json, data, headers, params, _url):

        """
        Helper function to process the request to Project Oxford

        Parameters:
        json: Used when processing images from its URL. See API Documentation
        data: Used when processing image read from disk. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        retries = 0
        result = None

        while True:

            response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

            if response.status_code == 429:

                print( "Message: %s" % ( response.json()['error']['message'] ) )

                if retries <= _maxNumRetries:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    print( 'Error: failed after retrying!' )
                    break

            elif response.status_code == 200 or response.status_code == 201:

                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                print( "Error code: %d" % ( response.status_code ) )
                print( "Message: %s" % ( response.json()['error']['message'] ) )

            break

        return result

    try:
        # Subscribe to the proxies services

        # We need this broker to be able to construct
        # NAOqi modules and subscribe to other modules
        # The broker must stay alive until the program exists
        myBroker = ALBroker("myBroker",
           "0.0.0.0",   # listen to anyone
           0,           # find a free port and use it
           NAO_IP,         # parent broker IP
           NAO_PORT)       # parent broker port


        # Warning: SpeachRec must be a global variable
        # The name given to the constructor must be the name of the
        # variable
        # global SpeachRec
        SpeachRec = SpeachRecModule("SpeachRec")

        #Getting the nao proxies
        video = ALProxy("ALVideoDevice")
        tts = ALProxy("ALTextToSpeech")

        # tts_service  = session.service("ALTextToSpeech")
        motion_service  = ALProxy("ALMotion")
        # animation_player_service = ALProxy("ALAnimationPlayer")

        asr_service = ALProxy("ALAnimatedSpeech")

        # set the local configuration
        configuration = {"bodyLanguageMode":"contextual"}


        if not motion_service.robotIsWakeUp():
            motion_service.wakeUp()


        # say the text with the local configuration
        asr_service.say("I am Multi-purpose Anthropomorphic Robot for Telepresence Assistance, but you can call me Marta!", configuration)
        #asr_service.say("Hello! ^start(animations/Stand/Gestures/Hey_1) Nice to meet you!")
        time.sleep(0.5)

        asr_service.say("Let's play a game called ^start(animations/Stand/Gestures/IDontKnow_1), I spy with my little eye.")

        def look_around(t):
            #look around
            names  = ["HeadPitch","HeadYaw"]
            angleLists  = [[-25.0*almath.TO_RAD, 25.0*almath.TO_RAD, -25.0*almath.TO_RAD, 0.0,],
                        [45.0*almath.TO_RAD, -45.0*almath.TO_RAD, 0.0]]
            timeLists   = [[1.0, 3.0, 5.0, 6.0], [ 2.0, 4.0, 6.0]]
            isAbsolute  = True
            motion_service.post.angleInterpolation(names, angleLists, timeLists, isAbsolute)
            time.sleep(t)

        def wrong_ans(t):
            #WRONG Answer animation
            asr_service.say("Wrong! ^start(animations/Stand/Gestures/No_3) You are embarrassingly bad at this game")
            time.sleep(t)

        def right_ans(t):
            #RiGHT Answer animation
            asr_service.say("Alright! ^start(animations/Stand/Gestures/Enthusiastic_5) alright, alright. You got this one!")
            time.sleep(t)

        try:
            #"Test_Video", CameraIndex=1, Resolution=1, ColorSpace=0, Fps=5
            #CameraIndex= 0(Top), 1(Bottom)
            #Resolution= 0(160*120), 1(320*240), VGA=2(640*480), 3(1280*960)
            #ColorSpace= AL::kYuvColorSpace (index=0, channels=1), AL::kYUV422ColorSpace (index=9,channels=3),
            #AL::kRGBColorSpace RGB (index=11, channels=3), AL::kBGRColorSpace BGR (to use in OpenCV) (index=13, channels=3)
            #Fps= OV7670 VGA camera can only run at 30, 15, 10 and 5fps. The MT9M114 HD camera run from 1 to 30fps.
            #Settings for resolution 1 (320x240)
            resolution_type = 1
            fps=10
            cam_w = 320
            cam_h = 240
            #Settigns for resolution 2 (320x240)
            #resolution_type = 2
            #fps = 15
            #cam_w = 640
            #cam_h = 480
            camera_name_id_top = video.subscribeCamera("TopCam", 0, resolution_type, 13, fps)

        except BaseException, err:
            print str(err)

        plt.ion()

        while True:
            # In this state it is captured a stream of images from
            # the NAO camera and it is convertend in a Numpy matrix
            #Get Images from camera
            #TopCam
            naoqi_img = video.getImageRemote(camera_name_id_top)
            if(naoqi_img != None):
                img = (
                       numpy.reshape(
                          numpy.frombuffer(naoqi_img[6], dtype='%iuint8' % naoqi_img[2]),
                          (naoqi_img[1], naoqi_img[0], naoqi_img[2])
                                  )
                       )
            else:
               img = numpy.zeros((cam_h, cam_w))
            img_top = numpy.copy(img)


            #Show the image
            plt.imshow(img[:,:,::-1])

            data = to_stream(img[:,:,::-1])


            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = _key_vision
            headers['Content-Type'] = 'application/octet-stream'

            json = None

            params = {'visualFeatures': 'Description', 'language': 'en'}

            result = processRequest( json, data, headers, params, _url_vision_analise)

            # https://westus.dev.cognitive.microsoft.com/docs/services/56ea598f778daf01942505ff/operations/56ea5a1cca73071fd4b102bb
            input_text = result['description']['captions'][0]['text']
            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = _key_ling

            body = {
                "language" : "en",
                "analyzerIds" : ["4fa79af1-f22c-408d-98bb-b7d7aeef7f04"],
                "text" : input_text}

            result = processRequest( body, None, headers, None, _url_linguistic)

            NN_list = list()
            for i,t in enumerate(result[0]['result'][0]):
                if t=='NN':
                    NN_list.append((input_text.split(' '))[i])

            r_idx = numpy.random.randint(0,high=len(NN_list))

            look_around(0.01)

            vocabulary = ["quit", "bye", "another", str(NN_list[r_idx])]
            tts.say("I spy with my little eye, something beginning with " + str(NN_list[r_idx][0]))
            tts.say("Can you guess what it is?")
            tts.say("You have five seconds to say it.")

            SpeachRec.my_set_vocabulary(vocabulary)
            plt.pause((60/20.)/10)
            time.sleep(5)
            SpeachRec.pause_speech_recognition(True)

            print "DEBUG:" + str(SpeachRec.word_from_nao)

            print "DEBUG:" + str(NN_list[r_idx])

            if SpeachRec.word_from_nao[0]==vocabulary[-1]:
                right_ans(0.01)
                tts.say("Well done! The word was "+vocabulary[-1])
            else:
                wrong_ans(0.01)
                languages_abr = ['pt','es','it','fr']
                languages = ['Portuguese','Spanish','Italian','French']
                hint = numpy.random.randint(0,high=len(languages_abr))
                tts.say("I will give you a hint.")
                try:
                    trans = mtranslate.translate(NN_list[r_idx],to_language=languages_abr[hint])
                except Exception, e:
                    trans = "Error"+str(e)
                tts.say("In "+languages[hint]+", they would say " + str(trans))
                tts.say("Can you guess now?")
                tts.say("You have five more seconds to say it.")
                # SpeachRec.change_language(languages[hint])

                SpeachRec.pause_speech_recognition(False)
                time.sleep(5)
                SpeachRec.pause_speech_recognition(True)

                if SpeachRec.word_from_nao[0]==vocabulary[-1]:
                    right_ans(0.01)
                    tts.say("Well done! The word was "+vocabulary[-1])
                else:
                    wrong_ans(0.01)                    
                    tts.say("Sorry, it was "+str(NN_list[r_idx]))

    except Exception, e:
        print "ERROR:" +str(e)

    finally:
        tts.say("I spy with my little eye, something beginning with S")
        tts.say("See you later! Bye.")

        video.unsubscribe(camera_name_id_top)

        SpeachRec.asr.setAudioExpression(False)
        SpeachRec.asr.setVisualExpression(False)
        SpeachRec.asr.unsubscribe("Test_ASR")
        motion_service.rest()
        myBroker.shutdown()
        sys.exit(0)


if __name__=="__main__":
    foo()
