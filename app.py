from flask import Flask, jsonify, request, send_from_directory
import subprocess
import os

app = Flask(__name__)
OUTPUT_DIR = "output"

@app.route('/')
def index():
    return '''
        <h2>MPD to M3U8 Converter</h2>
        <form method="POST" action="/convert">
            MPD URL: <input type="text" name="mpd"><br>
            ClearKey (format: key:iv): <input type="text" name="clearkey"><br>
            Cookie (__hdnea__ only): <input type="text" name="cookie"><br>
            <input type="submit" value="Convert">
        </form>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    mpd = request.form.get("mpd")
    clearkey = request.form.get("clearkey")
    cookie = request.form.get("cookie")
    
    if not mpd or not clearkey or not cookie:
        return jsonify({"error": "Missing parameters"}), 400

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Clean old files
    for f in os.listdir(OUTPUT_DIR):
        os.remove(os.path.join(OUTPUT_DIR, f))

    playlist_path = f"{OUTPUT_DIR}/playlist.m3u8"
    segment_pattern = f"{OUTPUT_DIR}/segment_%03d.ts"

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-user_agent", "plaYtv/7.1.3 (Linux;Android 13) ygx/69.1 ExoPlayerLib/824.0",
        "-headers", f"Cookie: {cookie}\r\n",
        "-decryption_key", clearkey,
        "-i", mpd,
        "-c", "copy",
        "-f", "hls",
        "-hls_time", "6",
        "-hls_segment_filename", segment_pattern,
        playlist_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        return jsonify({
            "status": "success",
            "m3u8_url": f"/output/playlist.m3u8"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "FFmpeg failed", "details": str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
