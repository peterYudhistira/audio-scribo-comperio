from scipy.io import wavfile
import noisereduce as nr
# load data
rate, data = wavfile.read("obamna.wav")
# perform noise reduction
reduced_noise = nr.reduce_noise(y=data, sr=rate)
wavfile.write("obamna2.wav", rate, reduced_noise)


