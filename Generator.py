import math
import wave
import struct

REAL_FREQ_DICT = {"0": 110, "1": 440} # maps hexdcimal digits to a pre decided freq
SINGLE_FREQ_DURATION = 2
SAMPLE_RATE = 44100
SAMPLE_WIDTH = 2 # in bytes

def generate_audio(s, output_file):
    # prepare wave file
    wf = wave.open(output_file, "w")
    wf.setnchannels(1)  # mono
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(SAMPLE_RATE)
    #convert str to matching freq
    real_freq_lst = []
    for c in s:
        real_freq_lst.append(REAL_FREQ_DICT[c])
    # generate a sin wave for each freq
    for freq in real_freq_lst:
        angular_freq = freq * math.pi * 2
        # generate frequencies
        for sample_num in range(SAMPLE_RATE * SINGLE_FREQ_DURATION):
            data = generate_sample(sample_num, angular_freq)
            wf.writeframesraw(data)

    wf.close()


def generate_sample(sample_num, angular_freq):
    sample_time = sample_num / SAMPLE_RATE
    sample_angle = sample_time * angular_freq
    return struct.pack('<h', int(32767 * math.sin(sample_angle)))

def main():
    generate_audio("1010", "test_wav.wav")

if __name__ == "__main__":
    main()