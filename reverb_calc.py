import librosa
from keras.models import load_model
import numpy as np
from bokeh.plotting import figure, output_file, show

model = load_model('model_reverb.h5')
filepath='rms.wav'
y, sr = y, sr = librosa.load(filepath)
print (type(y))
melgram = librosa.feature.melspectrogram(y=y, sr=sr)

print('melgram')
print (melgram.shape)
S_dB = librosa.power_to_db(melgram, ref=np.max)

window = np.int(44100 / 512)
hop = window #no overlap

n_of_instances = np.int(S_dB.shape[1] / hop)
print(n_of_instances)
set = np.zeros((n_of_instances, S_dB.shape[0], window))
print('set shape')
print (set.shape)

for i in range(0, n_of_instances - 3):
 set[i, :, :] = S_dB[:, i * hop: i*hop + window]

print(set.shape)
print(model.summary())

X = set.reshape(set.shape[0], set.shape[1], set.shape[2], 1)
predictions = model.predict(X)

print (predictions)

n_bars = set.shape[0]
wf = np.zeros((n_bars,))

for i in range(n_bars):
    wf[i] = predictions[i]
    if wf[i]>1:
        wf[i] = 1


p = figure(plot_width=400, plot_height=400, x_range=(0, n_bars), tools='pan,xwheel_zoom', active_scroll='xwheel_zoom',
           title='reverberation')
bottom = np.zeros((n_bars,))
left = np.arange(n_bars)
p.quad(top=wf, bottom=bottom, left=left, right=left + 1, color="#B3DE69")

show(p)
