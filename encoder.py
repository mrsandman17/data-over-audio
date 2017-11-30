import binascii
import logging
import math
import struct
import wave

import utils

# Channel_num in wav file. Set to mono, only mono channels are supported
CHANNELS = 1
# Bytes length of each sample in the wav file. Only width of 2 bytes is supported
SAMPLE_WIDTH = 2

class Encoder():

    def __init__(self, synchronizer):
        self.synchronizer = synchronizer
        # Get the freq dict
        self.freq_dict = utils.get_hex2freq_dict(self.synchronizer.min_freq, self.synchronizer.freq_difference)

    def encode(self, data, output_file):
        """
        Generates wave file of data
        :param data: the data to be encoded
        :param output_file: wave file name
        :return:
        """
        logging.info("Generating wav file based on data:\n'{0}'".format(data))
        logging.info("Preparing headers for wav file: {0}".format(output_file))
        with wave.open(output_file, "w") as wave_file:
            # Setup wave file headers
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(SAMPLE_WIDTH)
            wave_file.setframerate(self.synchronizer.sample_rate)
            logging.info("Converting data to hex".format(data))
            # Convert data to hex representation
            hex_data = binascii.hexlify(data.encode()).decode()
            logging.info("Mapping hex data to frequencies")
            # freq_lst holds the freq(Hz) for each hex digit
            # Convert each char to a freq and add to freq_list
            freq_lst = [self.freq_dict[c] for c in hex_data]
            logging.info("Inserting sync frequencies")
            freq_lst = self._get_synchronized_frequency_list(self.synchronizer.sync_freq, self.synchronizer.sync_repeat, freq_lst)
            logging.info("Frequencies to write:\n{0}".format(str(freq_lst)))
            logging.info("Writing {0} frequencies to wav (as sin waves)".format(len(freq_lst)))
            # Write all the frequencies in freq_lst to wave_file
            self._write_frequencies(wave_file, freq_lst)
            logging.info("Frequencies written successfully")
        return

    def _write_frequencies(self, wave_file, freq_lst):
        """
        Creates a sin wave for each frequency in freq_lst and writes it to wave_file
        :param wave_file:
        :param freq_lst:
        :return:
        """
        # Generate a sin wave for each freq
        for freq in freq_lst:
            angular_freq = freq * math.pi * 2
            # Generate samples of the sin wave for freq
            for sample_num in range(int(self.synchronizer.sample_rate * self.synchronizer.single_freq_duration)):
                sample_data = self._generate_sample(sample_num, angular_freq)
                wave_file.writeframesraw(sample_data)

    def _generate_sample(self, sample_num, angular_freq):
        """
        Generates a single sample
        :return: packed 2 byte sin() result
        """
        sample_time = sample_num / self.synchronizer.sample_rate
        sample_angle = sample_time * angular_freq
        # Get the sin() and pack into little endian 2 byte int
        return struct.pack('<h', int(32767 * math.sin(sample_angle)))

    def _get_synchronized_frequency_list(self, sync_freq, sync_repeat, freq_lst):
        """
        :param sync_freq: Synchronization frequency
        :param sync_repeat: Times to repeat the synchronization frequency
        :param freq_lst: List of frequencies to be edited
        :return: Synchronized frequency list
        """
        sync_frequencies = [sync_freq] * sync_repeat
        return sync_frequencies + freq_lst + sync_frequencies