
class Synchronizer():

    def __init__(self, min_freq, max_freq, freq_difference, sync_freq, sync_repeat):
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.freq_difference = freq_difference
        self.sync_freq = sync_freq
        self.sync_repeat = sync_repeat

    def get_freq_dict(self):
        """
        Generates and returns: hex digit -> freq dictionary
        """
        digits = 16
        return {hex(digit):self.min_freq + self.freq_difference * digit for digit in range(digits)}



    def insert_sync_freq(self, freq_lst):
        """
        SYNC_FREQ * SYNC_REPEAT | DATA | SYNC_FREQ * SYNC_REPEAT |
        """

        sync_frequencies = [self.sync_freq] * self.sync_repeat
        return sync_frequencies + freq_lst + sync_frequencies