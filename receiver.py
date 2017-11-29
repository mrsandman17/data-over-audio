"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import matplotlib.pyplot as plt
from scipy.fftpack import fft
import pyaudio
import wave
import struct
import numpy as np
import binascii
from recorder import Recorder
from synchronizer import Synchronizer

class WavDataReceiver():

    def __init__(self, synchronizer, sample_rate, single_freq_duration):
        self.synchronizer = synchronizer
        self.sample_rate = sample_rate
        self.single_freq_duration = single_freq_duration
        self.hex_dict = {v: k for k, v in synchronizer.get_freq_dict().items()}

    def _read_to_frequencies(self, wav_file):
        wav_file = wave.open(wav_file, 'r')
        # read to data and look for sync freq
        frames_red = self._read_to_data(wav_file, 10000, 5)
        # Change the chunk of data to read
        data_size = int(self.sample_rate * self.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        # read until the end of file
        for freq in self._receive_frames(wav_file, data_size, wav_file.getnframes() - frames_red):
            # reached end of data
            if prev_freq == self.synchronizer.sync_freq and freq == self.synchronizer.sync_freq:
                break
            prev_freq = freq
            if freq != self.synchronizer.sync_freq:
                freq_lst.append(int(freq))
        wav_file.close()
        return freq_lst

    def _read_to_data(self, wav_file, data_size, allowed_deviation):
        # start reading in small chunks to look for the sync frequency
        frames_red = 0
        # Find the first sync freq
        for freq in self._receive_frames(wav_file, data_size, wav_file.getnframes()):
            frames_red += data_size
            if self.synchronizer.sync_freq - allowed_deviation < freq < self.synchronizer.sync_freq + allowed_deviation:
                # Read until the beginning of data
                data_size = (data_size * self.synchronizer.sync_repeat) - data_size
                wav_file.readframes(data_size)
                frames_red += data_size
                return frames_red
        return frames_red

    def receive_data(self, wav_file):
        # read the bytes data to frequencies
        freq_lst = self._read_to_frequencies(wav_file)
        print(freq_lst)
        hexed_data = [self.hex_dict[i][2:]+self.hex_dict[j][2:] for i,j in zip(freq_lst[::2], freq_lst[1::2])]
        print(hexed_data)
        data = "".join([binascii.unhexlify(c).decode() for c in hexed_data])
        return data

    def _receive_frames(self, wav_file, data_size, frames_num):
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
        converts bytesdata (sin wave) data of size: data_size to a single frequency in hertz
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
    # #Set up recorder
    # wav_recorder = Recorder(record_format=pyaudio.paInt16, channels=1, sample_rate=44100, chunk_size=1024)
    # # Record 10 sec
    # wav_recorder.record_to_wav("test_wav_recorded_1.wav", 10)
    synchronizer = Synchronizer(min_freq=120, max_freq=6000, freq_difference=40, sync_freq=80, sync_repeat=2)
    data_receiver = WavDataReceiver(synchronizer, sample_rate=44100, single_freq_duration=0.5)
    print(data_receiver.receive_data("test_wav.wav"))


    # todo: convert a frequencey to hex
    # todo: testing
    # assemble frequencies array
    # convert the frequencies array to hex
    # convert hex to chars

if __name__ == "__main__":
    main()

