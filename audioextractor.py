import ffmpeg
def extract_audio (inputfilepath):
    input = ffmpeg.input(inputfilepath)
    input = input.audio
    outputfilepath = inputfilepath[:-3] + 'wav'
    input = ffmpeg.output(input,outputfilepath)
    ffmpeg.run(input)
    return outputfilepath