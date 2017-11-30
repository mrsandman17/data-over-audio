import json
import logging
import logging.config
import os
import sys

from encoder import WavDataEncoder


def main():
    data = sys.argv[1]
    output_file = sys.argv[2]
    setup_logging("log_config.json")
    logging.debug("Initializing")
    encoder = WavDataEncoder()
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