import pyaudio
import wave



class Recorder():

    def __init__(self, record_format, channels, sample_rate,chunk_size=1024):
        self.record_format = record_format
        self.channels = channels
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

    def record_to_wav(self, output_file_name, record_time):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.record_format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)

        print("* recording")

        frames = []

        for i in range(0, int(self.sample_rate / self.chunk_size * record_time)):
            data = stream.read(self.chunk_size)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(output_file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.record_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()