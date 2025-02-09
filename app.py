from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import cv2
import base64
from fingerprint_comparison import compare_fingerprints

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
SOUND_FOLDER = 'static/sounds'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SOUND_FOLDER'] = SOUND_FOLDER

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/compare', methods=['POST'])
def compare():
    # Check if files are included in the request
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'message': 'Both images are required for comparison.'}), 400

    file1 = request.files['image1']
    file2 = request.files['image2']

    # Check if files are selected
    if file1.filename == '' or file2.filename == '':
        return jsonify({'message': 'No file selected for uploading.'}), 400

    # Check file extensions
    if allowed_file(file1.filename) and allowed_file(file2.filename):
        filename1 = secure_filename(file1.filename)
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        file1.save(filepath1)

        filename2 = secure_filename(file2.filename)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        file2.save(filepath2)

        try:
            similarity_score, img1, img2 = compare_fingerprints(filepath1, filepath2)

            # Convert images to base64 for rendering in HTML
            img1_base64 = base64.b64encode(cv2.imencode('.png', img1)[1]).decode('utf-8')
            img2_base64 = base64.b64encode(cv2.imencode('.png', img2)[1]).decode('utf-8')

            # Determine sound to play based on similarity score
            sound_file = "access_granted.m4a" if similarity_score > 0.8 else "access_denied.m4a"

            return render_template(
                'result.html',
                similarity_score=similarity_score,
                img1=img1_base64,
                img2=img2_base64,
                sound_file=sound_file
            )
        except Exception as e:
            return jsonify({'message': f'Error occurred: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file format.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
