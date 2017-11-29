import math
import wave
import struct
import binascii
import logging
import os
import logging.config
import json
from synchronizer import Synchronizer

#todo: replace globals with class variables
#todo: add logging
#todo: add tests

class WavDataEncoder():

    def __init__(self, synchronizer):
        self.synchronizer = synchronizer
        # Get the freq dict
        self.freq_dict = synchronizer.get_hex2freq_dict()

    def encode(self, logger, data, output_file):
        """
        Generates wave file of data
        :param data: the data to be encoded
        :param output_file: wave file name
        :return:
        """
        logger.info("generating wav file based on data:\n'{0}'".format(data))
        logger.info("Preparing headers for wav file: {0}".format(output_file))
        wf = wave.open(output_file, "w")
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2) # 2 bytes sample width
        wf.setframerate(self.synchronizer.sample_rate)
        logger.debug("Converting data to hex".format(data))
        # Convert data to hex representation
        hex_data = binascii.hexlify(data.encode()).decode()
        logger.debug("Mapping hex data to frequencies")
        # freq_lst holds the freq(Hz) for each hex digit
        freq_lst = []
        # Convert str to matching freq
        for c in hex_data:
            # Convert each char to a freq and add to freq_list
            freq_lst.append(self.freq_dict['0x' + c])
        logger.debug("Inserting sync frequencies")
        freq_lst = self.synchronizer.insert_sync_freq(freq_lst)
        logger.info("Frequencies to write:\n{0}".format(str(freq_lst)))
        logger.info("Writing {0} frequencies to wav (as sin waves)".format(len(freq_lst)))
        # Write all the frequencies in freq_lst to wf
        self._write_frequencies(wf, freq_lst)
        logger.info("Frequencies written successfully")
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
            for sample_num in range(int(self.synchronizer.sample_rate * self.synchronizer.single_freq_duration)):
                sample_data = self._generate_sample(sample_num, angular_freq)
                wf.writeframesraw(sample_data)

    def _generate_sample(self, sample_num, angular_freq):
        """
        Generates a single sample
        :return: packed 2 byte sin() result
        """
        sample_time = sample_num / self.synchronizer.sample_rate
        sample_angle = sample_time * angular_freq
        # Get the sin() and pack into little endian 2 byte int
        return struct.pack('<h', int(32767 * math.sin(sample_angle)))
