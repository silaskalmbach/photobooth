from flask import Flask, request, render_template, jsonify, url_for, send_from_directory
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder and static serving
# UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = 'Background'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400

        if file and file.filename.lower().endswith('.jpg'):
            # Check if background.jpg exists and rename it
            background_path = os.path.join(app.config['UPLOAD_FOLDER'], 'background.jpg')
            if os.path.exists(background_path):
                timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                new_name = f'{timestamp}.jpg'
                os.rename(background_path, os.path.join(app.config['UPLOAD_FOLDER'], new_name))

            # Delete background.jpg if it exists
            if os.path.exists(background_path):
                os.remove(background_path)

            # Save new upload as background.jpg
            file.save(background_path)
            return jsonify({'message': 'File uploaded successfully'}), 200
        
        return jsonify({'message': 'Only .jpg files are allowed'}), 400

    return render_template('upload.html')

# Add route to serve images directly
@app.route('/Background/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/images')
def get_images():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.lower().endswith('.jpg'):
            files.append({
                'name': f,
                'path': url_for('uploaded_file', filename=f),
                'isBackground': f == 'background.jpg'
            })
    return jsonify(files)

# Add route to set background
@app.route('/set_background', methods=['POST'])
def set_background():
    data = request.get_json()
    selected_image = data.get('image')
    if selected_image:
        selected_path = os.path.join(app.config['UPLOAD_FOLDER'], selected_image)
        background_path = os.path.join(app.config['UPLOAD_FOLDER'], 'background.jpg')
        
        if os.path.exists(background_path):
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            new_name = f'{timestamp}.jpg'
            os.rename(background_path, os.path.join(app.config['UPLOAD_FOLDER'], new_name))
        
        os.rename(selected_path, background_path)
        return jsonify({'message': 'Background set successfully'}), 200
    
    return jsonify({'message': 'No image selected'}), 400

# Remove these lines as we're now using a dedicated route
# app.static_folder = os.path.abspath(UPLOAD_FOLDER)
# app.static_url_path = '/static'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
