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

@app.route('/Texture_mixing', methods=['POST'])
def texture_mixing():
    style1 = request.files['style1']
    style2 = request.files['style2']
    mixing_alpha = request.form['mixing_alpha']

    # Save the uploaded images to the static directory
    style1_path = f'static/style/{style1.filename}'
    style2_path = f'static/style/{style2.filename}'
    style1.save(style1_path)
    style2.save(style2_path)

    # Run the Python script for texture mixing using subprocess
    subprocess.run([
        'python', 'optex.py',
        '--style', style1_path, style2_path,
        '--mixing_alpha', mixing_alpha
    ])

    return redirect(url_for('index'))


@app.route('/Color_transfer', methods=['POST'])
def color_transfer():
    style = request.files['style']
    content = request.files['content']
    style_scale = request.form['style_scale']
    content_strength = request.form['content_strength']

    # Save the uploaded images to the static directory
    style_path = f'static/style/{style.filename}'
    content_path = f'static/content/{content.filename}'
    style.save(style_path)
    content.save(content_path)

    # Run the Python script for color transfer using subprocess
    subprocess.run([
        'python', 'optex.py',
        '--style', style_path,
        '--content', content_path,
        '--style_scale', style_scale,
        '--content_strength', content_strength,
        '--color_transfer', 'opt',
        '--size', '1024'
    ])

    return redirect(url_for('index'))


@app.route('/Texture_synthesis', methods=['POST'])
def texture_synthesis():
    style = request.files['style']
    size = request.form['size']

    # Save the uploaded style image to the static directory
    style_path = f'static/style/{style.filename}'
    style.save(style_path)

    # Run the Python script for texture synthesis using subprocess
    subprocess.run([
        'python', 'optex.py',
        '--style', style_path,
        '--size', size
    ])

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)




