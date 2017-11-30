import binascii
import logging
import struct
import wave

import numpy as np

import utils


class Decoder():

    def __init__(self, synchronizer):
        self.synchronizer = synchronizer
        # Get the freq dict: {Freq: hex}
        self.hex_dict = utils.get_freq2hex_dict(self.synchronizer.min_freq, self.synchronizer.freq_difference)

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
        """
        Converts a list of frequencies to ascii chars
        :param freq_lst:
        :return:
        """
        # Convert freq_lst to assembled_payload
        hex_data = self._to_hex(freq_lst)
        logging.info("Data as hex digits:\n{0}".format("".join(hex_data)))
        assembled_payload = self._to_ascii(hex_data)
        logging.info("Conversion Completed")
        return assembled_payload

    def _to_ascii(self, hex_data):
        """
        :param hex_data: Data to be converted
        :return: data in ascii
        """
        logging.info("Converting to ascii chars")
        # convert chars in hex format back to ascii
        assembled_data = ""
        for char_hex in hex_data:
            try:
                assembled_data += binascii.unhexlify(char_hex).decode()
            except UnicodeDecodeError:
                # The hex digits couldn't be converted to an ascii character
                logging.warning("Couldn't convert hexdigits: '{0}' to char (Unclear Frequency?)".format(char_hex))
                # Drop unknown char
                assembled_data += "?c?"
        return assembled_data

    def _to_hex(self, freq_lst):
        """
        Converts a freq list to a list of 2 sequential hex characters.
        Each frequency = hex character
        Freq -> Hex mapping is achieved with self.hex_dict
        :param freq_lst: List to to be converted
        :return: list of hex pairs
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
        """
        Finds and returns the frame number where the payload start
        :param wav_file:
        :return: the frame count
        """
        # read in chunks to look for the sync frequency
        frames_red = 0
        for freq in self._get_frequencies(wav_file, self.synchronizer.sync_search_chunk, wav_file.getnframes()):
            frames_red += self.synchronizer.sync_search_chunk
            # Calculate the allowed range
            min_sync_freq = self.synchronizer.sync_freq - self.synchronizer.sync_freq_deviation
            max_sync_freq = self.synchronizer.sync_freq + self.synchronizer.sync_freq_deviation
            # If the freq matches allowed range
            if min_sync_freq < freq < max_sync_freq:
                # Read until the beginning of data
                data_size = (self.synchronizer.sync_search_chunk * self.synchronizer.sync_repeat) - self.synchronizer.sync_search_chunk
                wav_file.readframes(data_size)
                frames_red += data_size
                return frames_red
        return frames_red

    def _get_payload(self, wav_file, frames_num):
        """
        reads from frames_num to sync freq.
        :param wav_file:
        :param frames_num: THe frame count where the payload starts
        :return: A list of the payload frequencies.
        """
        # Change the chunk of data to read
        data_size = int(self.synchronizer.sample_rate * self.synchronizer.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        for freq in self._get_frequencies(wav_file, data_size, frames_num):
            if prev_freq == self.synchronizer.sync_freq and freq == self.synchronizer.sync_freq:
                # reached end of data
                break
            prev_freq = freq
            if freq != self.synchronizer.sync_freq:
                # freq is a data frequency
                freq_lst.append(int(freq))
        return freq_lst

    def _get_frequencies(self, wav_file, data_size, frames_num):
        """
        Generator.
        Calculates the remaining frequencies number in wav_file.
        Reads data_size frames.
        Returns a frequency in Hz of the frames red.
        :param wav_file:
        :param data_size: size of each freq
        :param frames_num: Where to begin to read
        """
        # Get the number of frequencies in the message
        frequencies_num = int(frames_num / data_size)
        for freq_data in range(frequencies_num):
            data = wav_file.readframes(data_size)
            yield self._get_frequency(data, data_size)

    def _get_frequency(self, data, data_size):
        """
        Generates a frequency from raw bytes data using fft
        :param data: raw bytes data from wav file
        :param data_size: size of bytes data
        :return: A frequency (Hz)
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
