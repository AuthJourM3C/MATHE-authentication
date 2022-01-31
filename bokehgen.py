

def generatehtml(filepath):
    import numpy as np
    import librosa
    import mp3_encoder
    from bokeh.plotting import figure, output_file, show
    import matplotlib.pyplot as plt
    import os

    def rms(signal):
        rootms = np.sqrt(np.sum(signal ** 2) / len(signal))
        return rootms

    if os.path.isfile("./templates/temp/temp.html"):
        print("removing temp.html")
        os.remove("./templates/temp/temp.html")
    y, sr = librosa.load(filepath)
    y = librosa.to_mono(y)
    y = np.double(y)
    binwin = np.int(2048/4)

    wvlength = np.int(np.ceil(len(y) / binwin))


    wf = np.zeros((wvlength,))
    for i in range(wvlength):
        wf[i] = rms(y[i*binwin : (i+1)*binwin])



    p = figure(plot_width=400, plot_height=400, x_range= (0,wvlength),tools='pan,xwheel_zoom', active_scroll='xwheel_zoom',title='Audio RMS')
    bottom=np.zeros((wvlength,))
    left=np.arange(wvlength)
    p.quad(top=wf, bottom=bottom, left=left, right=left+1 ,color="#B3DE69")


    #featureextraction#############################################################
    wavoriginal, fs1 = librosa.load(filepath)
    double_filepath = mp3_encoder.wav2mp3(filepath)
    wavdouble, fs2 = librosa.load(double_filepath)

    fs1 = 2*fs1
    fs2 = 2*fs2

    import numpy as np
    wavdouble = np.double(wavdouble)
    wavoriginal = np.double(wavoriginal)


    hop_length = fs2

    mfccOrig=librosa.feature.mfcc(y=wavoriginal, sr=fs2,n_mfcc=40,n_fft=int(fs2), hop_length=hop_length)
    mfccDC=librosa.feature.mfcc(y=wavdouble,sr=fs1,n_mfcc=40,n_fft=int(fs1),hop_length=fs1)

    mfccDiff=np.abs(mfccOrig-mfccDC)

    differences=np.zeros((mfccOrig.shape[1],1))



    import scipy
    for i in range(mfccOrig.shape[1]):
        differences[i]=scipy.spatial.distance.euclidean(mfccOrig[:,i],mfccDC[:,i])

    deriv=np.gradient(differences, axis=0)






    deriv = deriv/max(np.abs(deriv));
    filtro=np.abs(deriv) < 0.25;
    deriv[filtro] = 0;


    deriv.reshape((deriv.shape[0],))

    deriv2=np.zeros((wvlength,1))
    j=0
    for i in range (deriv.shape[0]):
        deriv2[j]=deriv[i]
        j = j + np.int(hop_length/binwin)


    p2 = figure(plot_width=400, plot_height=400, x_range=p.x_range,tools='pan, xwheel_zoom', active_scroll='xwheel_zoom', title = 'Gradient of Double Compression Feature Distances')
    bottom=np.zeros((len(deriv2),))
    left=np.arange(len(deriv2))
    p2.quad(top=deriv2[:,0], bottom=bottom, left=left, right=left+1 , color="#B3DE69")



	#spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=1.0)
    if np.min(D)<0:
        D = D - np.min(D) + 1

    from bokeh.plotting import figure, show, output_file,save
    from bokeh.models.mappers import LogColorMapper

    color_mapper = LogColorMapper(palette="Viridis256")
    p3 = figure(plot_width=400, plot_height=400, y_range=(0,1025),x_range=p.x_range, tools='pan,xwheel_zoom', active_scroll='xwheel_zoom', title = 'Spectrogram')
    p3.image(image=[D],x=0,y=0,dw=[D.shape[1]],dh=[D.shape[0]],color_mapper=color_mapper,dilate=True)

	
    #mfccdifferences####################################################
    step = int(D.shape[1]/mfccDiff.shape[1])
    j=0
    mfccDiff2=np.ones((40,24728))
    for i in range(mfccDiff.shape[1]):
        for j in range(step):
            mfccDiff2[:,i*step+j]=mfccDiff[:,i]

    p4 = figure(plot_width=400, plot_height=400, y_range=(0,40),x_range=p.x_range, tools='pan,xwheel_zoom', active_scroll='xwheel_zoom', title = 'Double Compression Feature Differences')
    p4.image(image=[mfccDiff2],x=0,y=0,dw=[mfccDiff2.shape[1]],dh=[mfccDiff2.shape[0]],color_mapper=color_mapper,dilate=True)
    from bokeh.layouts import gridplot

    ######reverberatioonCNN
    from keras.models import load_model
    model = load_model('model_reverb.h5')
    #filepath = 'rms.wav'
    y, sr = librosa.load(filepath)
    melgram = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(melgram, ref=np.max)

    window = np.int(44100 / 512)
    hop = window  # no overlap

    n_of_instances = np.int(S_dB.shape[1] / hop)
    set = np.zeros((n_of_instances, S_dB.shape[0], window))

    for i in range(0, n_of_instances - 3):
        set[i, :, :] = S_dB[:, i * hop: i * hop + window]


    X = set.reshape(set.shape[0], set.shape[1], set.shape[2], 1)
    predictions = model.predict(X)

    n_bars = set.shape[0]
    wf = np.zeros((n_bars,))

    for i in range(n_bars):
        wf[i] = predictions[i]
        if wf[i] > 1:
            wf[i] = 1

    p5 = figure(plot_width=400, plot_height=400, x_range=(0, n_bars), tools='pan,xwheel_zoom',
               active_scroll='xwheel_zoom',
               title='reverberation')
    bottom = np.zeros((n_bars,))
    left = np.arange(n_bars)
    p5.quad(top=wf, bottom=bottom, left=left, right=left + 1, color="#B3DE69")

    ######plot_output
    gr=gridplot([[p, p2],[p3,p4],[p5,None]])
    output_file("./templates/temp/temp.html", title="Audio Authentication Analysis")
    save(gr)
    output_file("./files/temp/temp.html", title="Audio Authentication Analysis")
    save(gr)
