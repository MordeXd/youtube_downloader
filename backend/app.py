from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import uuid
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def seconds_to_hms(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

@app.route("/info", methods=["POST"])
def get_video_info():
    try:
        data = request.json
        url = data.get("url")
        print("🔗 URL received:", url)

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            video_formats = []
            audio_formats = []

            for f in formats:
                if f.get("vcodec") != "none" and f.get("acodec") != "none":
                    video_formats.append({
                        "format_id": f["format_id"],
                        "ext": f["ext"],
                        "resolution": f.get("resolution") or f"{f['height']}p",
                        "filesize": round((f.get("filesize") or 0) / 1024 / 1024, 1)
                    })
                elif f.get("vcodec") == "none" and f.get("acodec") != "none":
                    audio_formats.append({
                        "format_id": f["format_id"],
                        "ext": f["ext"],
                        "abr": f.get("abr", "N/A"),
                        "filesize": round((f.get("filesize") or 0) / 1024 / 1024, 1)
                    })

            response = {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": seconds_to_hms(info.get("duration", 0)),
                "video_formats": video_formats,
                "audio_formats": audio_formats
            }
            return jsonify(response)

    except Exception as e:
        print("❌ Error in /info:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.json
        url = data.get("url")
        format_id = data.get("format_id")
        file_type = data.get("type")

        filename = f"{uuid.uuid4()}.%(ext)s"
        output_path = os.path.join(DOWNLOAD_DIR, filename)

        ydl_opts = {
            'format': format_id,
            'outtmpl': output_path,
            'quiet': True,
            'merge_output_format': 'mp4' if file_type == "video" else 'mp3',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            actual_filename = ydl.prepare_filename(info)

        # Delay deletion of file
        def delete_file_later(filepath):
            time.sleep(20)
            if os.path.exists(filepath):
                os.remove(filepath)

        threading.Thread(target=delete_file_later, args=(actual_filename,)).start()

        return send_file(actual_filename, as_attachment=True)

    except Exception as e:
        print("❌ Error in /download:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ YouTube Downloader Backend Running"

if __name__ == "__main__":
    print("🚀 Flask running at http://127.0.0.1:5000")
    app.run(debug=True)
