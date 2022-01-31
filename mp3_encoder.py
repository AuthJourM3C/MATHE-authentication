#pip install pydub
#apt-get install ffmpeg

from pydub import AudioSegment
import os

def wav2mp3(inputfilepath):
    sound = AudioSegment.from_file(inputfilepath, format="wav")
    encoded_filepath = os.path.splitext(inputfilepath)[0]+".mp3"
    file_handle = sound.export(encoded_filepath, format="mp3", bitrate="192k")
    return encoded_filepath

def mp32wav(inputfilepath):
    sound = AudioSegment.from_file(inputfilepath, format="mp3")
    file_handle = sound.export("test_audio_encoded.mp3", format="wav")