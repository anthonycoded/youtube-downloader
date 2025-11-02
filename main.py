from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Allow all origins

SAVE_PATH = "C:/Users/barbe/videos"  # default save directory
os.makedirs(SAVE_PATH, exist_ok=True)

def resolution_sort_key(stream):
    res = stream['resolution']
    # Extract height if format is 'WIDTHxHEIGHT'
    if isinstance(res, str) and 'x' in res:
        res_number = int(res.split('x')[1])
    else:
        try:
            res_number = int(res)
        except:
            res_number = 0
    return -res_number, -int(stream.get('fps', 0))



@app.route('/get_streams', methods=['POST'])
def get_streams():
    try:
        data = request.json
        video_url = data.get("url")

        if not video_url:
            return jsonify({"error": "Missing URL"}), 400

        # yt-dlp options for metadata only
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestvideo+bestaudio/best'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

            # Filter MP4 formats and only video or audio+video streams
            streams = []
            for f in formats:
                if f.get('ext') == 'mp4' and f.get('filesize'):
                    streams.append({
                        "itag": f.get('format_id'),
                        "resolution": f.get('resolution') or f.get('height'),
                        "fps": f.get('fps') or 0,
                        "mime_type": f.get('acodec') + "/" + f.get('vcodec'),
                        "filesize": f.get('filesize')
                    })

            # Remove duplicates by resolution+fps
            unique_streams = {}
            for s in streams:
                key = (s['resolution'], s['fps'])
                if key not in unique_streams:
                    unique_streams[key] = s

            sorted_streams = sorted(unique_streams.values(), key=resolution_sort_key)


            return jsonify({"streams": sorted_streams}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get("url")
        itag = data.get("itag")
        save_path = data.get("save_path", SAVE_PATH)

        if not video_url or not itag:
            return jsonify({"error": "Missing URL or stream itag"}), 400

        os.makedirs(save_path, exist_ok=True)

        # yt-dlp download options
        ydl_opts = {
            'format': itag,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            output_file = ydl.prepare_filename(info)

        return jsonify({"message": "Download successful", "file": output_file}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
