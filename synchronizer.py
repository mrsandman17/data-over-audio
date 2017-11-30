
class Synchronizer():
    """
    Holds config for the data transfer between encoder and decoder
    """
    def __init__(self):
        self.sample_rate =44100
        # The duration each freq is played
        self.single_freq_duration = 0.5
        # Min freq to use
        self.min_freq = 120
        # Difference between every 2 consecutive frequencies
        self.freq_difference = 50
        # A unique freq, used to signal sync
        self.sync_freq = 80
        # Times to repeat the sync_freq
        self.sync_repeat = 2
        # The chunk of data the decoder should look for the first sync frequency
        self.sync_search_chunk = 10000
        # Defines the range in which the decoder accepts the sync frequency
        self.sync_freq_deviation = 5