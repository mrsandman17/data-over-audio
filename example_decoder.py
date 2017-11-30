import json
import logging
import logging.config
import os
import sys

import pyaudio

from decoder import Decoder
from recorder import Recorder
from synchronizer import Synchronizer


def main():
    record_time = int(sys.argv[1])
    output_file = sys.argv[2]
    setup_logging("log_config.json")
    logging.info("Initializing")
    wav_recorder = Recorder(record_format=pyaudio.paInt16,
                            channels=1,
                            sample_rate=Synchronizer.sample_rate,
                            chunk_size=1024)
    data_decoder = Decoder()
    wav_recorder.record_to_wav(output_file, record_time)
    data = data_decoder.decode(output_file)
    logging.info("Received data:\n{0}".format(data))

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