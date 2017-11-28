import math
import wave
import struct

#todo: replace globals with class variables
#todo: add logging
#todo: add tests


class WavDataGenerator():

    def __init__(self, single_freq_duration=1.0, sample_rate=44100):
        self.single_freq_duration = single_freq_duration
        self.sample_rate = sample_rate
        # Get the freq dict
        self.freq_dict = self._get_freq_dict(80, 40)

    def _get_freq_dict(self, start_freq, freq_difference):
        """
        :param freq_delimiter: The delimiter between every 2 frequencies.
        """
        digits = 16
        return {hex(digit):start_freq + freq_difference * digit for digit in range(digits)}

    def generate(self, data, output_file):
        """
        Generates wave file for data
        :param data: the data to be encoded
        :param output_file: wave file name
        :return:
        """

        # Prepare wave file
        #todo: add exception handling
        wf = wave.open(output_file, "w")
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2) # 2 bytes sample width
        wf.setframerate(self.sample_rate)
        # Convert data to hex representation
        hex_data = data.encode().hex()
        # Holds the real audio freq for each hex digit
        freq_lst = []
        # Convert str to matching freq
        for c in hex_data:
            # Convert each char to a freq and add to freq_list
            freq_lst.append(self.freq_dict['0x' + c])
        print(freq_lst)
        # Generate a sin wave for each freq
        for freq in freq_lst:
            angular_freq = freq * math.pi * 2
            # Generate samples of the sin wave for freq
            for sample_num in range(int(self.sample_rate * self.single_freq_duration)):
                sample_data = self._generate_sample(sample_num, angular_freq)
                wf.writeframesraw(sample_data)
        wf.close()


    def _generate_sample(self, sample_num, angular_freq):
        """
        Generates a single sample
        :param sample_num:
        :param angular_freq:
        :return: packed 2 byte sin() result
        """
        sample_time = sample_num / self.sample_rate
        sample_angle = sample_time * angular_freq
        # Get the sin() and pack into little endian 2 byte int
        return struct.pack('<h', int(32767 * math.sin(sample_angle)))



def main():
    # A simple test case
    generator = WavDataGenerator(single_freq_duration=0.5, sample_rate=44100)
    generator.generate("amit", "test_wav.wav")

if __name__ == "__main__":
    main()