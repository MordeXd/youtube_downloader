from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import re
import tempfile

app = Flask(__name__)

def clean_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")

def seconds_to_hms(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

@app.route('/info', methods=['POST'])
def video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        print("🔗 Received URL:", url)
        ydl_opts = {'quiet': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = []
            for f in info['formats']:
                if f.get('filesize') and f.get('vcodec') != 'none':
                    resolution = f.get('resolution') or f.get('format_note', '')
                    if '1080' in resolution or '720' in resolution or '480' in resolution or '360' in resolution:
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'resolution': resolution,
                            'filesize': round(f['filesize'] / (1024 * 1024), 2),  # MB
                            'has_audio': f.get('acodec') != 'none',
                        })

            return jsonify({
                'title': info.get('title'),
                'duration': seconds_to_hms(info.get('duration', 0)),
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            })

    except Exception as e:
        print("❌ Error in /info:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')

    if not url or not format_id:
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = clean_title(info.get('title', 'video'))
            ext = 'mp4'
            tmp_path = tempfile.gettempdir()
            filepath = os.path.join(tmp_path, f"{title}.{ext}")

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                print(f"📦 Downloading: {percent} at {speed} | ETA: {eta}")
            elif d['status'] == 'finished':
                print("✅ Download finished, preparing to send...")

        ydl_opts = {
            'format': f"{format_id}+bestaudio/best",
            'outtmpl': filepath,
            'merge_output_format': 'mp4',
            'quiet': True,
            'progress_hooks': [progress_hook],
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        response = send_file(filepath, as_attachment=True)

        @response.call_on_close
        def cleanup():
            try:
                os.remove(filepath)
                print(f"🧹 Deleted: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete file: {e}")

        return response

    except Exception as e:
        print("❌ Error in /download:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Flask running at http://127.0.0.1:5000")
    app.run(debug=True)
