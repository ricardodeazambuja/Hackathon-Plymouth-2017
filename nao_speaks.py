
from naoqi import ALProxy
import time

rec = audio = None

global rec, audio

robot_IP = "192.168.1.100"

robot_PORT = 9559


tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)

# ----------> Mute <----------
#if audio.isAudioOutMuted() == False:
#     audio.muteAudioOut(True)
# audio.muteAudioOut(False)



if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nao Speaks!")

    parser.add_argument("--text", help="A string.", type=str, default="Spocazzo", required=False) # This optional field is required


    args=parser.parse_args() # processes everything

    tts.say(args.text)
