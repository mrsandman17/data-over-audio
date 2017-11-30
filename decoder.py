import binascii
import logging
import struct
import wave

import numpy as np

import utils
from synchronizer import Synchronizer


class Decoder():

    def __init__(self):
        # Get the freq dict: {Freq: hex}
        self.hex_dict = utils.get_hex2freq_dict(Synchronizer.min_freq, Synchronizer.freq_difference)

    def decode(self, wav_file):
        """
        Decode payload in wav_file
        :param wav_file: input file
        :return: Decoded payload
        """
        logging.info("receiving data from {0}".format(wav_file))
        # Read the bytes data to frequencies
        logging.info("opening wav file")
        with wave.open(wav_file, 'r') as wav_file:
            # Read to payload and look for sync freq
            logging.info("Seeking sync freq in data")
            frames_red = self._get_payload_start(wav_file)
            # Read data
            logging.info("Reading payload frequencies")
            payload_freq_lst = self._get_payload(wav_file, wav_file.getnframes() - frames_red)
            logging.info("Frequencies red: \n{0}".format(str(payload_freq_lst)))
        payload = self._to_string(payload_freq_lst)
        return payload

    def _to_string(self, freq_lst):
        # Convert freq_lst to a assembled_payload
        hex_data = self._to_hex(freq_lst)
        logging.info("Data as hex digits:\n{0}".format("".join(hex_data)))
        assembled_data = self._to_ascii(hex_data)
        logging.info("Conversion Completed")
        return assembled_data

    def _to_ascii(self, hex_data):
        logging.info("Converting to ascii chars")
        # convert chars in hex format back to ascii
        assembled_data = ""
        for char_hex in hex_data:
            try:
                assembled_data += binascii.unhexlify(char_hex).decode()
            except UnicodeDecodeError:
                logging.warning("Couldn't convert hexdigits: '{0}' to char (Unclear Frequency)".format(char_hex))
                # Drop unknown char
                assembled_data += "?c?"
        return assembled_data

    def _to_hex(self, freq_lst):
        """

        :param freq_lst:
        :return:
        """
        hex_data = ""
        logging.info("Looking for legal frequencies")
        logging.info("Auto correcting frequencies")
        for freq in freq_lst:
            # Get the closest freq in hex_dict
            corrected_freq = min(self.hex_dict.keys(), key=lambda possible_freq: abs(possible_freq - freq))
            hex_data += self.hex_dict[corrected_freq]
        logging.info("Converting frequencies to hex digits")
        # Join 2 consecutive hex digits (2 hex digits = char)
        hexed_data = [i + j for i,j in zip(hex_data[::2], hex_data[1::2])]
        return hexed_data

    def _get_payload_start(self, wav_file):
        # read in chunks to look for the sync frequency
        frames_red = 0
        for freq in self._get_frequencies(wav_file, Synchronizer.sync_search_chunk, wav_file.getnframes()):
            frames_red += Synchronizer.sync_search_chunk
            # Calculate the allowed range
            min_sync_freq = Synchronizer.sync_freq - Synchronizer.sync_freq_deviation
            max_sync_freq = Synchronizer.sync_freq + Synchronizer.sync_freq_deviation
            # If the freq matches allowed range
            if min_sync_freq < freq < max_sync_freq:
                # Read until the beginning of data
                data_size = (Synchronizer.sync_search_chunk * Synchronizer.sync_repeat) - Synchronizer.sync_search_chunk
                wav_file.readframes(data_size)
                frames_red += data_size
                return frames_red
        return frames_red

    def _get_payload(self, wav_file, frames_num):
        # Change the chunk of data to read
        data_size = int(Synchronizer.sample_rate * Synchronizer.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        for freq in self._get_frequencies(wav_file, data_size, frames_num):
            if prev_freq == Synchronizer.sync_freq and freq == Synchronizer.sync_freq:
                # reached end of data
                break
            prev_freq = freq
            if freq != Synchronizer.sync_freq:
                # freq is a data frequency
                freq_lst.append(int(freq))
        return freq_lst

    def _get_frequencies(self, wav_file, data_size, frames_num):
        """
        Generates a freq
        """
        # Get the number of frequencies in the message
        frequencies_num = int(frames_num / data_size)
        for freq_data in range(frequencies_num):
            data = wav_file.readframes(data_size)
            yield self._get_frequency(data, data_size)

    def _get_frequency(self, data, data_size):
        """
        Converts bytes data (sin wave): data of size: data_size to a single frequency in hertz
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
