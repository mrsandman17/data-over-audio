"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import matplotlib.pyplot as plt
from scipy.fftpack import fft
import pyaudio
import wave
import struct
import numpy as np
from recorder import Recorder


class WavDataReceiver():

    def __init__(self, wav_file_name, sample_rate, single_freq_duration):
        self.wav_file_name = wav_file_name
        self.sample_rate = sample_rate
        self.single_freq_duration = single_freq_duration

    def receive_data(self):
        wav_file = wave.open(self.wav_file_name, 'r')
        data_size = int(self.sample_rate * self.single_freq_duration)
        for freq in self._receive_data_frames(wav_file, data_size, wav_file.getnframes()):
            print(freq)
        wav_file.close()

    def _receive_data_frames(self, wav_file, data_size, frames_num):
        """
        generates a freq
        """
        # get the number of frequencies in the message
        frequencies_num = int(frames_num / data_size)
        for freq_data in range(frequencies_num):
            data = wav_file.readframes(data_size)
            yield self._get_freq(data, data_size)

    def _get_freq(self, data, data_size):
        """
        converts data of size: data_size to a single frequency
        """
        # Convert data_size frames of byte data (Short)
        data = struct.unpack('{n}h'.format(n=data_size), data)
        data = np.array(data)
        w = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(w))
        # Find the peak in the coefficients
        idx = np.argmax(np.abs(w))
        freq = freqs[idx]
        freq_in_hertz = abs(freq * self.sample_rate)
        return freq_in_hertz


def main():
    # # Set up recorder
    # wav_recorder = Recorder(pyaudio.paInt16, 44100, 1024)
    # # Record 10 sec
    # wav_recorder.record_to_wav("test_wav.wav", 10)
    data_receiver = WavDataReceiver("test_wav.wav", 44100, 0.5)
    data_receiver.receive_data()


    # todo: convert a frequencey to hex
    # todo: sync with the first frequency of the message
    # assemble frequencies array
    # convert the frequencies array to hex
    # convert hex to chars

if __name__ == "__main__":
    main()

