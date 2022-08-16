# -*- coding = utf-8 -*-
# @Time:16/06/22 19:20
# @Author: Zheng Zeng
# @File: vosksr.py
# @Goal: To convert mp3 files to mono wav files and generate transcripts from them.
import json

from vosk import Model, KaldiRecognizer
#pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio

import pyaudio
import sys
import os
import wave
import audioop

from pydub import AudioSegment
'''
Used in adDetector.py to convert mp3 files to mono wav files
'''
def convert_data(infilepath):
    #need constant updating of the most updated ffmpeg package

    AudioSegment.converter = '/opt/homebrew/Cellar/ffmpeg/5.1/bin/ffmpeg'
    ds = infilepath[0:-3]+"wav"
    print(ds)
    #read in mp3 files
    sound  = AudioSegment.from_mp3(infilepath)
    sound.export(ds,format="wav")
    outfilepath  = infilepath[0:-4]+ "mono.wav"
    #start converting
    try:
        infile= wave.open(ds, "rb")
        outfile = wave.open(outfilepath,'wb')
        outfile.setnchannels(1)
        outfile.setsampwidth(infile.getsampwidth())
        outfile.setframerate(infile.getframerate())
        soundbytes = infile.readframes(infile.getnframes())
        print("frames read: {} length: {}".format(infile.getnframes(),len(soundbytes)))
        monosoundbytes = audioop.tomono(soundbytes,infile.getsampwidth(),1,1)
        outfile.writeframes(monosoundbytes)
        return outfilepath
    except Exception as e:
        print(e)
    finally:
        infile.close()
        outfile.close()


'''
Used to generate the transcript of the input audio file
Only used with single input and output
Cannot write different content to the same file otherwise it will overwrite the original one 
'''
def create_data(filepath,destination):
    model = Model(r"/Users/zhengzeng/Desktop/SchoolStuff/CMU/Summer2022/codes/vosk-model-small-en-us-0.15")


    wf = wave.open(filepath,'rb')


    # You can also specify the possible word or phrase list as JSON list, the order doesn't have to be strict
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    sentences = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            resultdict = json.loads(rec.Result())
            sentences.append(resultdict.get("text",""))
        else:

            print(rec.PartialResult())

    resultdict = json.loads(rec.FinalResult())
    sentences.append(resultdict.get("text",""))
    for sent in sentences:
        print(sent+".\n")
    if os.path.exists(destination):
        with open(destination, 'a+') as f:
            for sent in sentences:
                f.write(sent)
                f.write(".")
    print("finishing transcribing the audio.")



if __name__ == '__main__':
    print(os.getcwd())
    # convert_data("data/Medium.mp3")
    create_data("data/Medium_mono.wav","medium.txt")