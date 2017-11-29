
class Synchronizer():
# Holds data and functionality shared between generator and receiver
    def __init__(self, sample_rate, single_freq_duration, min_freq, max_freq, freq_difference, sync_freq, sync_repeat):
        self.sample_rate =sample_rate
        # The duration each freq is played
        self.single_freq_duration = single_freq_duration
        # Min freq to use
        self.min_freq = min_freq
        # Max freq to use
        self.max_freq = max_freq
        # Difference between every 2 consecutive frequencies
        self.freq_difference = freq_difference
        # A unique freq, used to signal sync
        self.sync_freq = sync_freq
        # Times to repeat the sync_freq
        self.sync_repeat = sync_repeat

    def get_hex2freq_dict(self):
        """
        Generates and returns: hex digit -> freq dictionary
        """
        digits = 16
        return {hex(digit):self.min_freq + self.freq_difference * digit for digit in range(digits)}

    def get_freq2hex_dict(self):
        """
        Generates and returns: freq -> hex digit dictionary
        """
        digits = 16
        return {self.min_freq + self.freq_difference * digit: hex(digit) for digit in range(digits)}


    def insert_sync_freq(self, freq_lst):
        """
        SYNC_FREQ * SYNC_REPEAT | DATA | SYNC_FREQ * SYNC_REPEAT |
        """

        sync_frequencies = [self.sync_freq] * self.sync_repeat
        return sync_frequencies + freq_lst + sync_frequencies