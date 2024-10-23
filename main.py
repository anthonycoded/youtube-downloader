from tkinter import PhotoImage

from PIL.ImageOps import expand
from pytubefix import YouTube
from customtkinter import *
from PIL import Image
import ffmpeg
import os

save_path = "C:/Users/barbe/videos"
test_url = "https://www.youtube.com/watch?v=VTB0_SBltDw"

app = CTk()
app.title("Youtube Downloader")
app.geometry("500x400")
#app.config(width=500, padx=30, pady=30)

img = CTkImage(Image.open("image.png"))
status = "Ready"
youtube_url = StringVar()
download_quality = StringVar()
available_streams = []
radio_buttons = []  # List to hold all the radio buttons
video_url = youtube_url.get()


def select_quality(quality: str):
    global download_quality
    download_quality = quality

def reset():
    global available_streams
    global frame
    global radio_buttons
    available_streams.clear()
    # Remove existing radio buttons from the frame
    for radio in radio_buttons:
        radio.destroy()

    radio_buttons.clear()  # Clear the list of radio buttons
    app.update()


def get_streams(var_name, index, value_if_allowed):
    try:
        reset()
        global  available_streams


        # Get video streams for user to choose from
        yt = YouTube(youtube_url.get())
        video_streams = yt.streams.filter(
            progressive=False,
            file_extension="webm",
            adaptive=True,
            only_video=True
        )


        #list streams in UI
        for stream in video_streams[:4]:
            print(stream.resolution)
            available_streams.append(stream)
            radio = CTkRadioButton(
                frame,
                text=f"{stream.resolution}/{stream.fps}fps",
                value=stream.itag,
                command=select_quality(stream),
                radiobutton_width=20,
                width=400,
                radiobutton_height=20,
                corner_radius=150,
                border_width_unchecked = 2,
                border_width_checked=2,
                border_color="blue",
                hover_color="green",
                fg_color="green",
                hover=True,
                text_color="white",
                font=("Helvetica", 16),
                state="normal",
                text_color_disabled="green"
            )
            radio.pack(padx=20, pady=5, fill=BOTH, expand=True)
            radio_buttons.append(radio)
        status_label.configure(text=f" Please select video quality.", text_color="#0ce889", height=22)
        app.update()

    except Exception as e:
        print(f"Error: {e}")
        status_label.configure(text=f"Error: Please enter a valid youtube url.", text_color="#e80c1e", height=22)
        reset()
        app.update()

def download_video():
    try:
        global status

        if download_quality:
            status_label.configure(text="Initializing Download", text_color="#0ce889", height=22)
            button.destroy()
            url_entry.delete(0, "end")
            app.update()

            yt = YouTube(video_url)

            #Get video stream
            video_stream = yt.streams.filter(progressive=False, file_extension="webm", adaptive=True,
                                             only_video=True)

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

            status_label.configure(text="Something went wrong", text_color="#e80c1e", height=22)
            app.update()


    except Exception as e:
        status_label.configure(text=f"Error: {e}", text_color="#e80c1e", height=22)
        app.update()


# logo = CTkImage()
# logo.place(relx=0.5, rely=0.1, anchor="center")
# canvas.create_image( image=img)

url_label = CTkLabel(app, text="Please enter a youtube video url.")
url_label.place(relx=0.5, rely=0.1, anchor="center")

url_entry = CTkEntry(app, width=400, textvariable=youtube_url)
url_entry.place(relx=0.5, rely=0.2, anchor="center")
url_entry.focus()

status_label = CTkLabel(app, text=status)
status_label.place(relx=0.5, rely=0.3, anchor="center")

frame = CTkFrame(app, width=400, height=150,)
frame.place(relx=0.5, rely=0.55, anchor="center", )

button = CTkButton(app, text="Download Video", command=download_video, corner_radius=25, image=img)
button.place(relx=0.5, rely=.85, anchor="center")#grid(row=7, column=2, padx=20, pady=10, )

youtube_url.trace("w", get_streams)

if __name__ == "__main__":
    app.mainloop()
