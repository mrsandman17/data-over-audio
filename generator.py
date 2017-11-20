import binascii
import math
import wave
import struct

#todo: replace globals with class variables
#todo: add logging
#todo: add tests


class WavGenerator():

    def __init__(self, single_freq_duration=2.0, sample_rate=44100):
        self.single_freq_duration = single_freq_duration
        self.sample_rate = sample_rate
        self.freq_dict = self._get_freq_dict(200, 20, "hex") # get the default real freq dict

    def _get_freq_dict(self, freq_delimiter, start_freq, mode):
        """

        :param mode:  hex: 16 digits
                      bin: 2 digits
        :return: freq dictionary
        """
        if mode is "hex":
            digits = 16
        elif mode is "bin":
            digits = 2
        else:
            raise ValueError("illegal mode")
        return {hex(digit):start_freq + freq_delimiter * digit for digit in range(digits)}

    def generate(self, data, output_file):
        """
        generates wave output_file for data
        :param data: teh data to be encoded
        :param output_file: wave file name
        :return:
        """
        # prepare wave file
        #todo: add exception handling
        wf = wave.open(output_file, "w")
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2) # 2 bytes sample width
        wf.setframerate(self.sample_rate)
        hex_data = data.encode().hex() # convert data to hex representation
        freq_lst = [] # holds the real audio freq for each hex digit
        # convert str to matching freq
        for c in hex_data:
            #convert each char to a freq and add to freq_list
            freq_lst.append(self.freq_dict['0x' + c])
        # generate a sin wave for each freq
        for freq in freq_lst:
            angular_freq = freq * math.pi * 2
            # generate frequencies
            for sample_num in range(int(self.sample_rate * self.single_freq_duration)):
                sample_data = self._generate_sample(sample_num, angular_freq)
                wf.writeframesraw(sample_data)
        wf.close()


    def _generate_sample(self, sample_num, angular_freq):
        """
        generates a single sample
        :param sample_num:
        :param angular_freq:
        :return: packed 2 byte sin() result
        """
        sample_time = sample_num / self.sample_rate
        sample_angle = sample_time * angular_freq
        return struct.pack('<h', int(32767 * math.sin(sample_angle)))



def main():
    # simple test case
    generator = WavGenerator(single_freq_duration=0.5, sample_rate=44100)
    generator.generate("shalom omri", "test_wav.wav")

if __name__ == "__main__":
    main()