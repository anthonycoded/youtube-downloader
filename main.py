from pytubefix import YouTube
import tkinter as tk
from tkinter import filedialog

save_path = "C:/Users/barbe/videos"


def download_video(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension="mp4")

        highest_res_stream = streams.get_highest_resolution()
        print("Downloading...")

        highest_res_stream.download(output_path=save_path)
        print(f"Video downloaded successfully {yt.title}")

    except Exception as e:
        print(e)


def open_file_dialog():
    folder = filedialog.askdirectory()
    if folder:
        print(f"Selected Folder: {folder}")
    return folder


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    video_url = input("Please enter a Youtube url: ")

    download_video(video_url)
