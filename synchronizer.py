
class Synchronizer():
# Holds config shared between encoder and decoder
    sample_rate =44100
    # The duration each freq is played
    single_freq_duration = 0.5
    # Min freq to use
    min_freq = 120
    # Difference between every 2 consecutive frequencies
    freq_difference = 50
    # A unique freq, used to signal sync
    sync_freq = 80
    # Times to repeat the sync_freq
    sync_repeat = 2