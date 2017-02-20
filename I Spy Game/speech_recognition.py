"""
Python interface to Nao's internal speech recognition.

Ricardo de Azambuja
http://ricardodeazambuja.com

Based on:
http://doc.aldebaran.com/1-14/dev/python/reacting_to_events.html
http://github.com/firefoxmetzger
"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

NAO_IP = "192.168.1.100"

NAO_PORT = 9559


# Global variable to store the SpeachRec module instance
SpeachRec = None

class SpeachRecModule(ALModule):
    """ A simple module able to react
    to facedetection events
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        self.word_from_nao = ["No output",0.0]

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setVolume(0.5)

        self.asr = ALProxy("ALSpeechRecognition")
        self.asr.pause(True)
        # vocabulary = ["yes", "no", "please", "hello"]
        # self.asr.setVocabulary(vocabulary, False)
        # self.asr.pause(False)
        self.asr.subscribe("ASR_External_Python")

        # Subscribe to the FaceDetected event:
        global memory
        self.memory = ALProxy("ALMemory")
        self.memory.subscribeToEvent("WordRecognized",
            "SpeachRec",
            "onWordDetected")

        self.asr.pause(True)


    def my_set_vocabulary(self, vocabulary = ["yes", "no", "please", "hello"]):
        self.asr.pause(True)
        self.asr.setVocabulary(vocabulary, False)
        self.asr.pause(False)

    def pause_speech_recognition(self,cmd):
        self.asr.pause(cmd)

    def change_language(self,lang):
        self.asr.setLanguage(lang)

    def onWordDetected(self, eventName, value, subscriberIdentifier):
        """ This will be called each time a face is
        detected.
        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        self.memory.unsubscribeToEvent("WordRecognized","SpeachRec")

        self.word_from_nao = value

        print "SpeachRecModule - DEBUG:" + str(value)

        # Subscribe again to the event
        self.memory.subscribeToEvent("WordRecognized","SpeachRec","onWordDetected")

def main():
    """ Main entry point
    """
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: SpeachRec must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SpeachRec
    SpeachRec = SpeachRecModule("SpeachRec")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"

        SpeachRec.asr.setAudioExpression(False)
        SpeachRec.asr.setVisualExpression(False)
        SpeachRec.asr.unsubscribe("ASR_External_Python")
        myBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
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
    SpeachRec.my_set_vocabulary(['yes','no','maybe'])
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"

        SpeachRec.asr.setAudioExpression(False)
        SpeachRec.asr.setVisualExpression(False)
        SpeachRec.asr.unsubscribe("ASR_External_Python")
        myBroker.shutdown()
        sys.exit(0)
