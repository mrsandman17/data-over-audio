
def get_hex2freq_dict(min_freq, freq_difference):
    """
    :param min_freq: The first frequency in freq list
    :param freq_difference: Difference between every two sequential frequencies
    :return: dict: {str hex_digit: int frequency}
    """
    digits = 16
    return {hex(digit): min_freq + freq_difference * digit for digit in range(digits)}


def get_freq2hex_dict(min_freq, freq_difference):
    """
    :param min_freq: The first frequency in freq list
    :param freq_difference: Difference between every two sequential frequencies
    :return: dict: {int freq: str hex_digit}
    """
    digits = 16
    return {min_freq + freq_difference * digit: hex(digit) for digit in range(digits)}


def get_synchronized_frequency_list(sync_freq, sync_repeat, freq_lst):
    """
    :param sync_freq: Synchronization frequency
    :param sync_repeat: Times to repeat the synchronization frequency
    :param freq_lst: List of frequencies to be edited
    :return: Synchronized frequency list
    """
    sync_frequencies = [sync_freq] * sync_repeat
    return sync_frequencies + freq_lst + sync_frequencies