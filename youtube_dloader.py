from pytube import YouTube
def download(link):
# link = 'https://www.youtube.com/watch?v=YRTp7IJt7sw&list=PLW_2S5uJ4UA4SEgKfodFoYf02Ekkg6VLq'
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    # print(yt.title)
    stream.download('./files/videos/')
    filename = './files/videos/'+str(yt.title)+'.mp4'
    return filename

