# -*- coding = utf-8 -*-
# @Time:16/06/22 19:20
# @Author: Zheng Zeng
# @Goal: 1. convert mp3 files to mono wave files usiing the vosksr.py
# 2. detect advertisement in the audio file and remove them by chunking
# 3. get the transcription of each chunk and write them to a destination.
import audioop
import json
import os.path
import wave

from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

import chunkAudio as ca
from vosksr import convert_data,create_data
import adetector as adt
from mutagen.mp3 import  MP3
def main():
    print(os.getcwd())

    # print(data)
    file ="data/Medium.mp3"
    wav_file = convert_data(file) #convert mp3 file  to mono wav file
    remove_ad(wav_file)
    '''
     to go through a list of audio files
    file = "data\Medium" #a directory
    data_folder = os.path.join(os.getcwd(),path)
    data = list(os.walk(data_folder))
    for root, file, files in data:
        for name in files:
            filepath = os.path.join(root,name)
            wav_file = convert_data(filepath)
            remove_ad(wav_file)
            print("finished file name is %s" % name)
    '''

'''
to get the advertisement period using the aDetector packages
return the timestamps of the predicted advertisement
'''
def get_ads_period(file,threshold =0.85, ma =20):
    sound = AudioSegment.from_wav(file)
    length = len(sound)
    print("The length of the audio file is %s " % length)
    removal  = adt.core.audio2features(file,max_duration=length)
    timestamps , probs= adt.core.find_ads(removal,T=threshold,n=ma,show= False)
    print("Ads were detected at the following timestamps:")
    print(timestamps)
    print("Ad probabilities for these timestamps are:")
    print(probs)
    return timestamps
'''
The main function to take the output of a mono wav file
use other functions
'''
def remove_ad(wav_file_path):
    timestamps = get_ads_period(wav_file_path,threshold=0.85,ma = 10)
    sound = AudioSegment.from_wav(wav_file_path)
    begin = 0
    end = len(sound)
    chunks = []
    #get file name
    prefix =wav_file_path[0:-8].split('/')[-1]
    i = 0
    #read mono wav file from the source directory
    try:
        os.mkdir('S-DATA-Mono')
    except(FileExistsError):
        pass
    os.chdir('S-DATA-Mono')
    print(os.getcwd())

    for interval in timestamps: #[[1,20],[40,60]]
        pre = interval[0]
        exit = interval[1]
        chunk =sound[begin:pre]
        #get chunk file names
        chunk_file_name = prefix+"chunk {0}".format(i)+"mono.wav"
        #append the file names for further reading
        chunks.append(chunk_file_name)
        #export them to the mono directory
        chunk.export(chunk_file_name,format='wav')
        if exit<end:
            begin = exit
        i+=1
    #at the end
    #chunk the last one
    chunk = sound[exit:end]
    chunk_file_name = os.path.join(os.getcwd(),prefix + "chunk{0}".format(i) + "mono.wav")
    chunks.append(chunk_file_name)
    chunk.export(chunk_file_name, format='wav')
    #vosk transcription
    print("Start transcripting the list of chunks")
    os.chdir("../")
    print(os.getcwd())
    #redirect to the text directory
    try:
        os.mkdir('S-data-TEXT-R')
    except(FileExistsError):
        pass
    finally:
        os.chdir('S-data-TEXT-R')

    #create the destination name
    destination_path = os.path.join(os.getcwd(),prefix+".txt")
    #to store the result text
    result = []
    #a list of mono wav file paths
    for chunk_file_name in chunks:
        try:
            #acquire the transcripts of each chunk
            sentences = transcribe_with_vosk(chunk_file_name)
            result.extend(sentences) #append them to the list
            print("Finishing transcribing %s" % prefix )
        except Exception as e:
            print(e)
    #write the whole transcript to the destination
    write_to_txt(result,destination_path)

def transcribe_with_vosk(chunk_file_name):
    #chunks is a list of chunked wav object
    sentences = []
    wf = wave.open(chunk_file_name,'rb')
    model = Model(
        r"/Users/zhengzeng/Desktop/SchoolStuff/CMU/Summer2022/codes/vosk-model-small-en-us-0.15")
    print(os.getcwd())
    recognizer = KaldiRecognizer(model, wf.getframerate())
    recognizer.SetWords(True)
    print("Start dealing with %s" % chunk_file_name)
    try:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    resultdict = json.loads(recognizer.Result())
                    sentences.append(resultdict.get("text", ""))
                else:

                    print(recognizer.PartialResult())

            resultdict = json.loads(recognizer.FinalResult())
            sentences.append(resultdict.get("text", ""))
            for sent in sentences:
                print(sent + ".\n")
            return sentences
    except Exception as e:
            print(e)
    finally:
            print("Finished transcribing this chunk.")


def write_to_txt(sentences, destination = "transcript.txt"):
    write_to = os.path.join(os.getcwd(),destination)
    try:
        with open(write_to, 'w+') as f:
            for sent in sentences:
                f.write(sent)
                f.write(".")

    except Exception as e:
        print(e)
    finally:
        f.close()
    print("finish writing it to %s" % destination)

if __name__ == '__main__':
    main()