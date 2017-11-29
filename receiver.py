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

    def __init__(self, synchronizer, sync_search_chunk, sync_freq_deviation, auto_correct_frequencies):
        self.synchronizer = synchronizer
        # The chunk of data to look for the first sync frequency
        self.sync_search_chunk = sync_search_chunk
        # Defines the range in which the sync frequency is accepted
        self.sync_freq_deviation = sync_freq_deviation
        self.auto_correct_frequencies = auto_correct_frequencies
        # Get the freq dict: {Freq: hex}
        self.hex_dict = synchronizer.get_freq2hex_dict()

    def receive(self, wav_file):
        # Read the bytes data to frequencies
        freq_lst = self._read_frequencies(wav_file)
        print(freq_lst)
        data = self._convert_to_str(freq_lst)
        return data

    def _convert_to_str(self, freq_lst):
        # Convert every frequency to hex
        hexed_data = ""
        for freq in freq_lst:
            if self.auto_correct_frequencies:
                # Get the closest freq in hex_dict
                corrected_freq = min(self.hex_dict.keys(), key=lambda possible_freq: abs(possible_freq - freq))
                hexed_data += self.hex_dict[corrected_freq][2:]
            else:
                try:
                    hexed_data += self.hex_dict[freq][2:]
                # Frequency is unmapped
                except KeyError:
                    # Drop hex digits that translates to an unknown char
                    hexed_data += "e0"
        # Join 2 consecutive hex digits (2 hex digits = char)
        hexed_data = [i + j for i,j in zip(hexed_data[::2], hexed_data[1::2])]
        print(hexed_data)
        # convert chars in hex format back to ascii
        assembled_data = ""
        for char_hex in hexed_data:
            try:
                assembled_data += binascii.unhexlify(char_hex).decode()
            except UnicodeDecodeError:
                assembled_data += "?c?"
        return assembled_data

    def _read_frequencies(self, wav_file):
        wav_file = wave.open(wav_file, 'r')
        # Read to data and look for sync freq
        frames_red = self._read_until_data(wav_file)
        # Read data
        freq_lst = self._read_data_frequencies(wav_file, wav_file.getnframes() - frames_red)
        wav_file.close()
        return freq_lst

    def _read_data_frequencies(self, wav_file, frames_num):
        # Change the chunk of data to read
        data_size = int(self.synchronizer.sample_rate * self.synchronizer.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        # read until the end of file
        for freq in self._receive_frames(wav_file, data_size, frames_num):
            # reached end of data
            if prev_freq == self.synchronizer.sync_freq and freq == self.synchronizer.sync_freq:
                break
            prev_freq = freq
            if freq != self.synchronizer.sync_freq:
                freq_lst.append(int(freq))
        return freq_lst

    def _read_until_data(self, wav_file):
        # read in small chunks to look for the sync frequency
        frames_red = 0
        # Find the first sync freq
        for freq in self._receive_frames(wav_file, self.sync_search_chunk, wav_file.getnframes()):
            frames_red += self.sync_search_chunk
            # Calculate the allowed range
            min_sync_freq = self.synchronizer.sync_freq - self.sync_freq_deviation
            max_sync_freq = self.synchronizer.sync_freq + self.sync_freq_deviation
            # If the freq matches allowed range
            if min_sync_freq < freq < max_sync_freq:
                # Read until the beginning of data
                data_size = (self.sync_search_chunk * self.synchronizer.sync_repeat) - self.sync_search_chunk
                wav_file.readframes(data_size)
                frames_red += data_size
                return frames_red
        return frames_red

    def _receive_frames(self, wav_file, data_size, frames_num):
        """
        Generates a freq
        """
        # Get the number of frequencies in the message
        frequencies_num = int(frames_num / data_size)
        for freq_data in range(frequencies_num):
            data = wav_file.readframes(data_size)
            yield self._get_freq(data, data_size)

    def _get_freq(self, data, data_size):
        """
        Converts bytesdata (sin wave): data of size: data_size to a single frequency in hertz
        """
        # Convert data_size frames of byte data (Short)
        data = struct.unpack('{n}h'.format(n=data_size), data)
        data = np.array(data)
        w = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(w))
        # Find the peak in the coefficients
        idx = np.argmax(np.abs(w))
        freq = freqs[idx]
        freq_in_hertz = abs(freq * self.synchronizer.sample_rate)
        return freq_in_hertz


def main():
    output_file = r"generated_audio_samples\rec_sample_safe_config.wav"
    wav_recorder = Recorder(record_format=pyaudio.paInt16,
                            channels=1,
                            sample_rate=44100,
                            chunk_size=1024)
    # Record
    wav_recorder.record_to_wav(output_file, 20)
    synchronizer = Synchronizer(sample_rate=44100,
                                single_freq_duration=0.5,
                                min_freq=120,
                                freq_difference=50,
                                sync_freq=80,
                                sync_repeat=2)

    data_receiver = WavDataReceiver(synchronizer,
                                    sync_search_chunk=10000,
                                    sync_freq_deviation=5,
                                    auto_correct_frequencies=True)

    print(data_receiver.receive(output_file))
    #todo: logging


if __name__ == "__main__":
    main()

