
def get_hex2freq_dict(min_freq, freq_difference):
    """
    generates a dict, used to map between hexdigits to frequencies
    :param min_freq: The first frequency in freq list
    :param freq_difference: Difference between every two sequential frequencies
    :return: dict: {str hex_digit: int frequency}
    """
    digits = 16
    return {hex(digit)[2:]: min_freq + freq_difference * digit for digit in range(digits)}


def get_freq2hex_dict(min_freq, freq_difference):
    """
    generates a dict, used to map between frequencies and hexdigits
    :param min_freq: The first frequency in freq list
    :param freq_difference: Difference between every two sequential frequencies
    :return: dict: {int freq: str hex_digit}
    """
    digits = 16
    return {min_freq + freq_difference * digit: hex(digit)[2:] for digit in range(digits)}