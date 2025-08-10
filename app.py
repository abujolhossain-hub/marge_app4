from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp/uploads"
MERGED_FOLDER = "/tmp/merged"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_and_merge():
    files = request.files.getlist('videos')
    if not files or len(files) < 2:
        return jsonify({"error": "Please upload at least 2 videos"}), 400

    video_clips = []
    saved_files = []

    try:
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            saved_files.append(filepath)
        
        for path in saved_files:
            clip = VideoFileClip(path)
            video_clips.append(clip)
        
        final_clip = concatenate_videoclips(video_clips)
        output_path = os.path.join(MERGED_FOLDER, "merged_video.mp4")
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        for clip in video_clips:
            clip.close()
        final_clip.close()
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
