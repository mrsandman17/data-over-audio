import binascii
import logging
import struct
import wave

import numpy as np

import utils
from synchronizer import Synchronizer


class Decoder():

    def __init__(self, sync_search_chunk, sync_freq_deviation, auto_correct_frequencies):
        # The chunk of data to look for the first sync frequency
        self.sync_search_chunk = sync_search_chunk
        # Defines the range in which the sync frequency is accepted
        self.sync_freq_deviation = sync_freq_deviation
        self.auto_correct_frequencies = auto_correct_frequencies
        # Get the freq dict: {Freq: hex}
        self.hex_dict = utils.get_hex2freq_dict(Synchronizer.min_freq, Synchronizer.freq_difference)

    def decode(self, wav_file):
        logging.info("receiving data from {0}".format(wav_file))
        # Read the bytes data to frequencies
        freq_lst = self._read_frequencies(wav_file)
        logging.info("Frequencies red: \n{0}".format(str(freq_lst)))
        data = self._convert_to_str(freq_lst)
        return data

    def _convert_to_str(self, freq_lst):
        # Convert freq_lst to a assembled_data
        hexed_data = ""
        logging.debug("Looking for legal frequencies")
        if self.auto_correct_frequencies:
            logging.debug("Auto correcting frequencies")
            for freq in freq_lst:
                # Get the closest freq in hex_dict
                corrected_freq = min(self.hex_dict.keys(), key=lambda possible_freq: abs(possible_freq - freq))
                hexed_data += self.hex_dict[corrected_freq]
        else:
            for freq in freq_lst:
                try:
                    hexed_data += self.hex_dict[freq]
                except KeyError:
                    # Frequency is unmapped
                    logging.warning("Couldn't find exact frequency for: {0}".format(freq))
                    # Drop hex digits that translates to an unknown char
                    hexed_data += "e0"
        logging.debug("Converting frequencies to hex digits")
        # Join 2 consecutive hex digits (2 hex digits = char)
        hexed_data = [i + j for i,j in zip(hexed_data[::2], hexed_data[1::2])]
        logging.debug("Data as hex digits:\n{0}".format("".join(hexed_data)))
        logging.info("Converting to normal chars")
        # convert chars in hex format back to ascii
        assembled_data = ""
        for char_hex in hexed_data:
            try:
                assembled_data += binascii.unhexlify(char_hex).decode()
            except UnicodeDecodeError:
                logging.warning("Couldn't convert hexdigits: '{0}' to char (Unclear Frequency)".format(char_hex))
                # Drop unknown char
                assembled_data += "?c?"
        logging.debug("Conversion Completed")
        return assembled_data

    def _read_frequencies(self, wav_file):
        logging.debug("opening wav file")
        wav_file = wave.open(wav_file, 'r')
        # Read to data and look for sync freq
        logging.debug("Seeking sync freq in data")
        frames_red = self._read_until_data(wav_file)
        # Read data
        logging.debug("Reading data frequencies")
        freq_lst = self._read_data_frequencies(wav_file, wav_file.getnframes() - frames_red)
        wav_file.close()
        return freq_lst

    def _read_until_data(self, wav_file):
        # read in chunks to look for the sync frequency
        frames_red = 0
        for freq in self._receive_frames(wav_file, self.sync_search_chunk, wav_file.getnframes()):
            frames_red += self.sync_search_chunk
            # Calculate the allowed range
            min_sync_freq = Synchronizer.sync_freq - self.sync_freq_deviation
            max_sync_freq = Synchronizer.sync_freq + self.sync_freq_deviation
            # If the freq matches allowed range
            if min_sync_freq < freq < max_sync_freq:
                # Read until the beginning of data
                data_size = (self.sync_search_chunk * Synchronizer.sync_repeat) - self.sync_search_chunk
                wav_file.readframes(data_size)
                frames_red += data_size
                return frames_red
        return frames_red

    def _read_data_frequencies(self, wav_file, frames_num):
        # Change the chunk of data to read
        data_size = int(Synchronizer.sample_rate * Synchronizer.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        for freq in self._receive_frames(wav_file, data_size, frames_num):
            if prev_freq == Synchronizer.sync_freq and freq == Synchronizer.sync_freq:
                # reached end of data
                break
            prev_freq = freq
            if freq != Synchronizer.sync_freq:
                # freq is a data frequency
                freq_lst.append(int(freq))
        return freq_lst

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
        freq_in_hertz = abs(freq * Synchronizer.sample_rate)
        return freq_in_hertz
