from pytubefix import YouTube
import tkinter as tk
from tkinter import filedialog
import ffmpeg
import os

save_path = "C:/Users/barbe/videos"
#test_url = "https://www.youtube.com/watch?v=VTB0_SBltDw"

def download_video():
    try:
        video_url = input("Please enter a Youtube url: ")
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(progressive=False, file_extension="webm", adaptive=True, only_video=True).get_highest_resolution(progressive=False)
        audio_stream = yt.streams.filter(progressive=False, file_extension="webm", adaptive=True, only_audio=True)[0]

        print("Downloading video...")
        video_file= video_stream.download(output_path=save_path, filename=f"video-{yt.title}webm", )

        print(f"Downloading audio...")
        audio_file = audio_stream.download(output_path=save_path, filename=f"audio-{yt.title}webm")
#        print(audio_file)
        merge_audio_video(title=yt.title, audio_file=audio_file, video_file=video_file)
        #
        #
        # highest_res_stream.download(output_path=save_path)


    except Exception as e:
        print(e)


def open_file_dialog():
    folder = filedialog.askdirectory()
    if folder:
        print(f"Selected Folder: {folder}")
    return folder


def merge_audio_video(audio_file, video_file, title):
    print("Processing downloaded media...")
    try:
        video = ffmpeg.input(filename=video_file,).video
        audio = ffmpeg.input( filename=audio_file,).audio

        result = ffmpeg.output(
            audio,
            video,
            filename=f"{save_path}/{title}.mp4",
            vcodec='copy',
            acodec="aac",
            format="mp4"
        ).run()

        print ("Finishing up...")

        if result:
           os.remove(audio_file)
           os.remove(video_file)
           print(f"Video downloaded successfully {title}")
        else:
            print("Something went wrong")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()



    download_video()
