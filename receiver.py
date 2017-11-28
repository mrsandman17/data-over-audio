"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import matplotlib.pyplot as plt
from scipy.fftpack import fft
import pyaudio
import wave
import struct
import numpy as np


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "test_wav.wav"
SINGLE_FREQUENCY_DURATION = 0.5

def record():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def get_freq():

    frate = 44100.0
    data_size = int(frate / SINGLE_FREQUENCY_DURATION)
    wav_file = wave.open(WAVE_OUTPUT_FILENAME, 'r')
    data = wav_file.readframes(data_size)
    wav_file.close()
    # convert data_size frames of data in short
    data = struct.unpack('{n}h'.format(n=data_size), data)
    data = np.array(data)

    w = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(w))
    print(freqs.min(), freqs.max())
    # (-0.5, 0.499975)

    # Find the peak in the coefficients
    idx = np.argmax(np.abs(w))
    freq = freqs[idx]
    freq_in_hertz = abs(freq * frate)
    print(freq_in_hertz)
    # 439.8975


def main():
    pass
    get_freq()
    # todo: read a frequnciey manually
    # todo: read a few frequencies
    # todo: convert a frequencey to hex
    # find the first frequency
    # assamble  frequencies array
    # convert the frequencies array to hex
    # convert hex to chars

if __name__ == "__main__":
    main()

