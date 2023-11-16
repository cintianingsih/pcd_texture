from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

    return redirect(url_for('index'))

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




