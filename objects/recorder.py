import sounddevice as sd
import soundfile as sf
import wavio as wv
import queue
import keyboard
class AudioRecorder:
    def __init__(self) -> None:
        self.q = queue.Queue()

    def callback(self, indata, frames, time, status):
        self.q.put(indata.copy())

    def recordSomething(self, sampleRate, fileName, channels):
        fileName = "audios/"+fileName+".wav"
        sd.default.device = sd.query_devices(6)["name"]
        with sf.SoundFile(fileName, mode='x', samplerate=sampleRate,  # open a file with soundfile to write the recording in.
                          channels=channels) as file:
            with sd.InputStream(samplerate=sampleRate,  # begin recording
                                channels=channels, callback=self.callback):
                print('#' * 80)
                print('press space to stop the recording')
                print('#' * 80)
                while True:
                    file.write(self.q.get())
                    if keyboard.is_pressed('space'):
                        print("we savin {}".format(fileName))
                        break


# recorder = AudioRecorder()
# recorder.recordSomething(44100, input("file name : "), 2)
