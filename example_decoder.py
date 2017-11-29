import logging
import os
import logging.config
import json
import pyaudio
import sys
from recorder import Recorder
from decoder import WavDataDecoder
from synchronizer import Synchronizer

def main():
    record_time = int(sys.argv[1])
    output_file = sys.argv[2]
    logger = setup_logging("log_config.json")
    logger.debug("Initializing")
    wav_recorder = Recorder(record_format=pyaudio.paInt16,
                            channels=1,
                            sample_rate=44100,
                            chunk_size=1024)
    synchronizer = Synchronizer(sample_rate=44100,
                                single_freq_duration=0.5,
                                min_freq=120,
                                freq_difference=50,
                                sync_freq=80,
                                sync_repeat=2)
    data_decoder = WavDataDecoder(synchronizer,
                                    sync_search_chunk=10000,
                                    sync_freq_deviation=5,
                                    auto_correct_frequencies=True)
    wav_recorder.record_to_wav(logger, output_file, record_time)
    data = data_decoder.decode(logger, output_file)
    logger.info("Received data:\n{0}".format(data))

def setup_logging(config_path):
    """Setup logging configuration

    """
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        raise FileNotFoundError("config_path not found")
    return logging.getLogger()

if __name__ == "__main__":
    main()