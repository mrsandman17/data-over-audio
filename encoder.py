import binascii
import logging
import math
import struct
import wave

import utils
from synchronizer import Synchronizer

# Channel_num in wav file. Set to mono, only mono channels are supported
CHANNELS = 1
# Bytes length of each sample in the wav file. Only width of 2 bytes is supported
SAMPLE_WIDTH = 2

class Encoder():

    def __init__(self):
        # Get the freq dict
        self.freq_dict = utils.get_hex2freq_dict(Synchronizer.min_freq, Synchronizer.freq_difference)

    def encode(self, data, output_file):
        """
        Generates wave file of data
        :param data: the data to be encoded
        :param output_file: wave file name
        :return:
        """
        logging.info("Generating wav file based on data:\n'{0}'".format(data))
        logging.info("Preparing headers for wav file: {0}".format(output_file))
        wf = wave.open(output_file, "w")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(Synchronizer.sample_rate)
        logging.debug("Converting data to hex".format(data))
        # Convert data to hex representation
        hex_data = binascii.hexlify(data.encode()).decode()
        logging.debug("Mapping hex data to frequencies")
        # freq_lst holds the freq(Hz) for each hex digit
        freq_lst = []
        # Convert str to matching freq
        for c in hex_data:
            # Convert each char to a freq and add to freq_list
            freq_lst.append(self.freq_dict[c])
        logging.debug("Inserting sync frequencies")
        freq_lst = utils.get_synchronized_frequency_list(Synchronizer.sync_freq, Synchronizer.sync_repeat, freq_lst)
        logging.info("Frequencies to write:\n{0}".format(str(freq_lst)))
        logging.info("Writing {0} frequencies to wav (as sin waves)".format(len(freq_lst)))
        # Write all the frequencies in freq_lst to wf
        self._write_frequencies(wf, freq_lst)
        logging.info("Frequencies written successfully")
        wf.close()

    def _write_frequencies(self, wf, freq_lst):
        """
        Creates a sin wave for each frequency in freq_lst and writes it to wf
        :param wf:
        :param freq_lst:
        :return:
        """
        # Generate a sin wave for each freq
        for freq in freq_lst:
            angular_freq = freq * math.pi * 2
            # Generate samples of the sin wave for freq
            for sample_num in range(int(Synchronizer.sample_rate * Synchronizer.single_freq_duration)):
                sample_data = self._generate_sample(sample_num, angular_freq)
                wf.writeframesraw(sample_data)

    def _generate_sample(self, sample_num, angular_freq):
        """
        Generates a single sample
        :return: packed 2 byte sin() result
        """
        sample_time = sample_num / Synchronizer.sample_rate
        sample_angle = sample_time * angular_freq
        # Get the sin() and pack into little endian 2 byte int
        return struct.pack('<h', int(32767 * math.sin(sample_angle)))
