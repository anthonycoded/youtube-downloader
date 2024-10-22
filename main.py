from tkinter import PhotoImage

from pytubefix import YouTube
from customtkinter import *
from PIL import Image
import ffmpeg
import os

save_path = "C:/Users/barbe/videos"
#test_url = "https://www.youtube.com/watch?v=VTB0_SBltDw"

app = CTk()
app.title("Youtube Downloader")
app.geometry("500x400")
#app.config(width=500, padx=30, pady=30)

img = CTkImage(Image.open("image.png"))

status = "Ready"


def download_video():
    try:
        global status
        video_url = youtube_url.get()

        if len(video_url) > 0:
            status_label.configure(text="Initializing Download", text_color="#0ce889", height=22)
            button.destroy()
            url_entry.delete(0, "end")
            app.update()

            yt = YouTube(video_url)
            video_stream = yt.streams.filter(progressive=False, file_extension="webm", adaptive=True,
                                             only_video=True).get_highest_resolution(progressive=False)
            audio_stream = yt.streams.filter(progressive=False, file_extension="webm", adaptive=True, only_audio=True)[
                0]

            status_label.configure(text="Downloading video...", text_color="#0ce889", height=22)
            app.update()
            video_file = video_stream.download(output_path=save_path, filename=f"video-{yt.title}webm", )

            status_label.configure(text="Downloading audio...", text_color="#0ce889", height=22)
            app.update()
            audio_file = audio_stream.download(output_path=save_path, filename=f"audio-{yt.title}webm")
            merge_audio_video(title=yt.title, audio_file=audio_file, video_file=video_file)
        else:
            status_label.configure(text="Please enter a valid url.", text_color="#ed0909", height=22)
            app.update()
    except Exception as e:

        status_label.configure(text=f"Error: {e}", text_color="#ed0909", height=22)
        app.update()



def merge_audio_video(audio_file, video_file, title):
    global button
    status_label.configure(text="Reformatting downloaded media...", text_color="#0ce889", height=22)
    app.update()
    try:
        video = ffmpeg.input(filename=video_file, ).video
        audio = ffmpeg.input(filename=audio_file, ).audio

        result = ffmpeg.output(
            audio,
            video,
            filename=f"{save_path}/{title}.mp4",
            vcodec='copy',
            acodec="aac",
            format="mp4"
        ).run()

        print("Finishing up...")

        if result:
            os.remove(audio_file)
            os.remove(video_file)
            status_label.configure(text=f"Video downloaded successfully {title}", text_color="#0ce889", height=22, width=300)
            button = CTkButton(app, text="Download Video", command=download_video, corner_radius=25, image=img)
            button.place(relx=0.5, rely=0.5, anchor="center")
            app.update()


        else:

            status_label.configure(text="Something went wrong", text_color="#0ce889", height=22)
            app.update()


    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="#0ce889", height=22)
        app.update()


youtube_url = StringVar()
# logo = CTkImage()
# logo.place(relx=0.5, rely=0.1, anchor="center")
# canvas.create_image( image=img)

url_label = CTkLabel(app, text="Please enter a youtube video url.")
url_label.place(relx=0.5, rely=0.1, anchor="center")

url_entry = CTkEntry(app, width=400, textvariable=youtube_url,)
url_entry.place(relx=0.5, rely=0.2, anchor="center")
url_entry.focus()

status_label = CTkLabel(app, text=status)
status_label.place(relx=0.5, rely=0.3, anchor="center")

button = CTkButton(app, text="Download Video", command=download_video, corner_radius=25, image=img)
button.place(relx=0.5, rely=0.5, anchor="center")#grid(row=7, column=2, padx=20, pady=10, )

if __name__ == "__main__":
    app.mainloop()
