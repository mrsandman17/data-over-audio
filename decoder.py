import wave
import struct
import numpy as np
import binascii


class WavDataDecoder():

    def __init__(self, synchronizer, sync_search_chunk, sync_freq_deviation, auto_correct_frequencies):
        self.synchronizer = synchronizer
        # The chunk of data to look for the first sync frequency
        self.sync_search_chunk = sync_search_chunk
        # Defines the range in which the sync frequency is accepted
        self.sync_freq_deviation = sync_freq_deviation
        self.auto_correct_frequencies = auto_correct_frequencies
        # Get the freq dict: {Freq: hex}
        self.hex_dict = synchronizer.get_freq2hex_dict()

    def decode(self, logger, wav_file):
        logger.info("receiving data from {0}".format(wav_file))
        # Read the bytes data to frequencies
        freq_lst = self._read_frequencies(logger, wav_file)
        logger.info("Frequencies red: \n{0}".format(str(freq_lst)))
        data = self._convert_to_str(logger, freq_lst)
        return data

    def _convert_to_str(self, logger, freq_lst):
        # Convert freq_lst to a assembled_data
        hexed_data = ""
        logger.debug("Looking for legal frequencies")
        if self.auto_correct_frequencies:
            logger.debug("Auto correcting frequencies")
            for freq in freq_lst:
                # Get the closest freq in hex_dict
                corrected_freq = min(self.hex_dict.keys(), key=lambda possible_freq: abs(possible_freq - freq))
                hexed_data += self.hex_dict[corrected_freq][2:]
        else:
            for freq in freq_lst:
                try:
                    hexed_data += self.hex_dict[freq][2:]
                except KeyError:
                    # Frequency is unmapped
                    logger.warning("Couldn't find exact frequency for: {0}".format(freq))
                    # Drop hex digits that translates to an unknown char
                    hexed_data += "e0"
        logger.debug("Converting frequencies to hex digits")
        # Join 2 consecutive hex digits (2 hex digits = char)
        hexed_data = [i + j for i,j in zip(hexed_data[::2], hexed_data[1::2])]
        logger.debug("Data as hex digits:\n{0}".format("".join(hexed_data)))
        logger.info("Converting to normal chars")
        # convert chars in hex format back to ascii
        assembled_data = ""
        for char_hex in hexed_data:
            try:
                assembled_data += binascii.unhexlify(char_hex).decode()
            except UnicodeDecodeError:
                logger.warning("Couldn't convert {0} to char".format(char_hex))
                # Drop unknown char
                assembled_data += "?c?"
        logger.debug("Conversion Completed")
        return assembled_data

    def _read_frequencies(self, logger, wav_file):
        logger.debug("opening wav file")
        wav_file = wave.open(wav_file, 'r')
        # Read to data and look for sync freq
        logger.debug("Seeking sync freq in data")
        frames_red = self._read_until_data(wav_file)
        # Read data
        logger.debug("Reading data frequencies")
        freq_lst = self._read_data_frequencies(wav_file, wav_file.getnframes() - frames_red)
        wav_file.close()
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

    def _read_data_frequencies(self, wav_file, frames_num):
        # Change the chunk of data to read
        data_size = int(self.synchronizer.sample_rate * self.synchronizer.single_freq_duration)
        # Read data frames
        prev_freq = 0
        freq_lst = []
        for freq in self._receive_frames(wav_file, data_size, frames_num):
            if prev_freq == self.synchronizer.sync_freq and freq == self.synchronizer.sync_freq:
                # reached end of data
                break
            prev_freq = freq
            if freq != self.synchronizer.sync_freq:
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
        freq_in_hertz = abs(freq * self.synchronizer.sample_rate)
        return freq_in_hertz

#todo: configure logger so it isn't required