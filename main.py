from pytube import Stream
from pytubefix import YouTube
from customtkinter import *
from PIL import Image
import ffmpeg
import os

from pytubefix.cli import on_progress

save_path = ""
test_url = "https://www.youtube.com/watch?v=VTB0_SBltDw"

app = CTk()
app.title("Youtube Downloader")
app.geometry("500x400")
#app.config(width=500, padx=30, pady=30)

img = CTkImage(Image.open("image.png"))
status = "Ready"
youtube_url = StringVar()
download_quality = Stream
available_streams = []
radio_buttons = []  # List to hold all the radio buttons
video_url = ""

#bad_chars_list to sanitize video title/filename
bad_chars = [';', ':', '!', "*", "?", ".", '"', "|"]

# Progress Bars for Video and Audio
video_progress_bar = None
audio_progress_bar = None

# Initialize global variables for video and audio progress
video_bytes_remaining = 0
audio_bytes_remaining = 0


def select_quality(selected):
    global download_quality
    download_quality = selected

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


# Calculate percentage progress
def percent(tem, total):
    perc = (float(tem) / float(total)) * float(100)
    return perc


# Progress callback function for video and audio
def video_progress_function(stream, chunk, bytes_remaining):
    global video_bytes_remaining
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    video_bytes_remaining = bytes_remaining
    percentage = int((bytes_downloaded / total_size) * 100)

    video_progress_bar.set(percentage / 100)
    app.update()


def audio_progress_function(stream, chunk, bytes_remaining):
    global audio_bytes_remaining
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    audio_bytes_remaining = bytes_remaining
    percentage = int((bytes_downloaded / total_size) * 100)

    audio_progress_bar.set(percentage / 100)
    app.update()


def get_streams(var_name, index, value_if_allowed):
    try:
        reset()
        global available_streams
        global video_url
        global url_label

        # Get video streams for user to choose from
        yt = YouTube(youtube_url.get())
        video_url = youtube_url.get()

        video_streams = yt.streams.filter(
            progressive=False,
            file_extension="webm",
            adaptive=True,
            only_video=True
        )

        #list streams in UI
        for stream in video_streams[:4]:
          #  print(stream.resolution)
            available_streams.append(stream)
            radio = CTkRadioButton(
                frame,
                text=f"{stream.resolution}/{stream.fps}fps",
                value=stream,
                command=lambda s=stream: select_quality(s),
                radiobutton_width=20,
                width=400,
                radiobutton_height=20,
                corner_radius=150,
                border_width_unchecked=2,
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
        global download_quality
        global video_url

        url_label.configure(text="Please wait, your video is being downloaded")
        app.update()

        if download_quality and video_url:
            status_label.configure(text="Initializing Download", text_color="#0ce889", height=22)
            button.destroy()
            url_entry.delete(0, "end")
            app.update()

            yt_video = YouTube(video_url, on_progress_callback=video_progress_function)  # Separate object for video
            yt_audio = YouTube(video_url, on_progress_callback=audio_progress_function)  # Separate object for audio

            title = yt_video.title
            for char in bad_chars:
                title = title.replace(char, '')

            # Explicitly get the video stream from yt_video
            video_stream = yt_video.streams.get_by_itag(download_quality.itag)

            audio_stream = yt_audio.streams.filter(progressive=False, file_extension="webm", adaptive=True, only_audio=True)[0]

            status_label.configure(text="Downloading video...", text_color="#0ce889", height=22)
            app.update()
            video_file = video_stream.download(output_path=save_path, filename=f"video-{title}.webm")

            status_label.configure(text="Downloading audio...", text_color="#0ce889", height=22)
            app.update()
            audio_file = audio_stream.download(output_path=save_path, filename=f"audio-{title}.webm")

            merge_audio_video(title=title, audio_file=audio_file, video_file=video_file)
        else:
            status_label.configure(text="Please enter a valid URL.", text_color="#ed0909", height=22)
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

        print("Cleaning up...")

        if result:
            os.remove(audio_file)
            os.remove(video_file)
            status_label.configure(text=f"Video downloaded successfully {title}", text_color="#0ce889", height=22,
                                   width=200, )
            button = CTkButton(app, text="Download Video", command=download_video, corner_radius=25, image=img)
            button.place(relx=0.5, rely=0.5, anchor="center")
            url_label.configure(text="Please enter a youtube video url.")
            app.update()
            print("Download completed. Status: Ready")


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


frame = CTkFrame(app, width=400, height=150, )
frame.place(relx=0.5, rely=0.55, anchor="center", )

# Video Progress Bar
video_progress_bar = CTkProgressBar(frame, width=200, height=25, corner_radius=30, progress_color="green")
video_progress_bar.pack()
video_progress_bar.set(0.0)

# Audio Progress Bar
audio_progress_bar = CTkProgressBar(frame, width=200, height=25, corner_radius=30, progress_color="blue")
audio_progress_bar.pack(pady=10)
audio_progress_bar.set(0.0)

button = CTkButton(frame, text="Download Video", command=download_video, corner_radius=25, image=img)
button.pack()  #grid(row=7, column=2, padx=20, pady=10, )

youtube_url.trace("w", get_streams)

if __name__ == "__main__":
    app.mainloop()
