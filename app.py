import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    latest_image = session.get('latest_image', None)
    return render_template('index.html', latest_image=latest_image)

@app.route('/generate', methods=['POST'])
def generate_texture():
    style = request.files['style']
    content = request.files['content']
    content_strength = request.form['content_strength']

    # Save the uploaded images to the static directory
    style_path = f'static/style/{style.filename}'
    content_path = f'static/content/{content.filename}'
    style.save(style_path)
    content.save(content_path)

    # Run the Python script using subprocess
    subprocess.run([
        'python', 'optex.py',
        '--style', style_path,
        '--content', content_path,
        '--content_strength', content_strength
    ])
     # Get the latest generated image dynamically
    latest_image = get_latest_generated_image()

    # Store the latest processed image filename in the session
    session['latest_image'] = latest_image

    return redirect(url_for('index'))

def get_latest_generated_image():
    output_folder = 'output'
    generated_images = [filename for filename in os.listdir(output_folder) if filename.endswith('.png')]
    
    # Sort filenames based on the time they were last modified
    generated_images.sort(key=lambda x: os.path.getmtime(os.path.join(output_folder, x)), reverse=True)

    return generated_images[0] if generated_images else None

@app.route('/generated/<filename>')
def serve_generated_image(filename):
    return send_from_directory('output', filename)

    
if __name__ == '__main__':
    app.run(debug=True)




