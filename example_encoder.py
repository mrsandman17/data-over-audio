import json
import logging
import logging.config
import os
import sys

from encoder import WavDataEncoder
from synchronizer import Synchronizer


def main():
    data = sys.argv[1]
    output_file = sys.argv[2]
    setup_logging("log_config.json")
    logging.debug("Initializing")
    # set up synchronizer
    synchronizer = Synchronizer(sample_rate=44100,
                                single_freq_duration=0.5,
                                min_freq=120,
                                freq_difference=50,
                                sync_freq=80,
                                sync_repeat=2)
    encoder = WavDataEncoder(synchronizer)
    encoder.encode(data, output_file)

def setup_logging(config_path):
    """Setup logging configuration
    """
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        raise FileNotFoundError("config_path not found")

if __name__ == "__main__":
    main()