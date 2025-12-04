#!/usr/bin/env python3
"""
Cosmos Predict 2.5 - Simple Image2World Web Interface
A streamlined Flask app for generating videos from images using Cosmos Predict.
"""

import os
import json
import uuid
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'cosmos-predict-simple-web-interface-2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Authentication setup
auth = HTTPBasicAuth()
AUTH_USERNAME = 'admin'
AUTH_PASSWORD = 'cosmos2025'
users = {AUTH_USERNAME: generate_password_hash(AUTH_PASSWORD)}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Directory configuration
BASE_DIR = Path(__file__).parent.absolute()
UPLOAD_FOLDER = BASE_DIR / 'uploads'
OUTPUT_FOLDER = BASE_DIR / 'outputs'
LOG_FOLDER = BASE_DIR / 'logs'
PROJECT_ROOT = BASE_DIR.parent

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Global job tracking
generation_status = {}

# Default negative prompt
DEFAULT_NEGATIVE_PROMPT = "drone, aerial flight, hovering, camera dolly, camera moving forward, zooming camera, floating robot, flying robot, distorted wheels, morphing shape, shaky camera, motion blur on background, changing background geometry."


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def run_inference(job_id, json_config_path, output_dir):
    """Run Cosmos Predict inference as subprocess"""
    inference_script = PROJECT_ROOT / 'examples' / 'inference.py'

    cmd = [
        'python3',
        str(inference_script),
        '-i', str(json_config_path),
        '-o', str(output_dir),
        '--offload_diffusion_model',
        '--offload_tokenizer',
        '--offload_text_encoder'
    ]

    # Set environment variable for better CUDA memory management
    env = os.environ.copy()
    env['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

    try:
        # Run subprocess with streaming output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
            env=env
        )

        # Stream output line by line
        for line in process.stdout:
            clean_line = line.strip()
            if clean_line:
                generation_status[job_id]['output_lines'].append(clean_line)

                # Try to extract progress if available
                if 'progress' in clean_line.lower() or '%' in clean_line:
                    try:
                        # Look for percentage in output
                        if '%' in clean_line:
                            percent_str = clean_line.split('%')[0].split()[-1]
                            progress = int(float(percent_str))
                            generation_status[job_id]['progress'] = min(progress, 99)
                    except (ValueError, IndexError):
                        pass

        process.wait()

        if process.returncode != 0:
            raise Exception(f"Inference failed with return code {process.returncode}")

    except Exception as e:
        raise Exception(f"Inference execution error: {str(e)}")


def generate_video_async(job_id, image_path, settings):
    """Async function to generate video (runs in thread)"""
    try:
        # Update status: starting
        generation_status[job_id]['status'] = 'starting'
        generation_status[job_id]['stage'] = 'Creating configuration...'

        # Create output directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"img2world_{timestamp}"
        output_dir = OUTPUT_FOLDER / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create JSON config
        config = {
            "inference_type": "image2world",
            "name": output_name,
            "input_path": str(Path(image_path).absolute()),
            "prompt": settings['prompt'],
            "negative_prompt": settings['negative_prompt'],
            "enable_autoregressive": settings['enable_autoregressive'],
            "num_output_frames": settings['num_output_frames'],
            "chunk_size": settings['chunk_size'],
            "chunk_overlap": settings['chunk_overlap'],
            "resolution": settings['resolution'],
            "seed": settings['seed'],
            "guidance": settings['guidance']
        }

        json_file = output_dir / 'config.json'
        with open(json_file, 'w') as f:
            json.dump(config, f, indent=2)

        generation_status[job_id]['json_config'] = str(json_file.relative_to(OUTPUT_FOLDER))

        # Update status: generating
        generation_status[job_id]['status'] = 'generating'
        generation_status[job_id]['stage'] = 'Running Cosmos Predict inference... This may take several minutes.'
        generation_status[job_id]['progress'] = 5

        # Run inference
        run_inference(job_id, json_file, output_dir)

        # Find generated video
        video_files = list(output_dir.glob('*.mp4'))
        if not video_files:
            raise Exception("No video file generated. Check console output for details.")

        video_file = video_files[0]
        generation_status[job_id]['video_file'] = str(video_file.relative_to(OUTPUT_FOLDER))
        generation_status[job_id]['status'] = 'completed'
        generation_status[job_id]['stage'] = 'Video generation complete!'
        generation_status[job_id]['progress'] = 100

    except Exception as e:
        generation_status[job_id]['status'] = 'failed'
        generation_status[job_id]['error'] = str(e)
        generation_status[job_id]['stage'] = f'Error: {str(e)}'
        generation_status[job_id]['output_lines'].append(f'ERROR: {str(e)}')


# Routes

@app.route('/')
@auth.login_required
def index():
    """Main page with upload form"""
    return render_template('index.html',
                         default_negative_prompt=DEFAULT_NEGATIVE_PROMPT)


@app.route('/generate', methods=['POST'])
@auth.login_required
def generate():
    """Handle video generation request"""
    try:
        # Validate image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or WEBP'}), 400

        # Generate unique job ID
        job_id = uuid.uuid4().hex[:12]

        # Save uploaded image
        filename = secure_filename(file.filename)
        image_filename = f"{job_id}_{filename}"
        image_path = UPLOAD_FOLDER / image_filename
        file.save(image_path)

        # Parse form parameters
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        negative_prompt = request.form.get('negative_prompt', DEFAULT_NEGATIVE_PROMPT).strip()

        # Parse numeric parameters with defaults
        try:
            num_output_frames = int(request.form.get('num_output_frames', 77))
            chunk_size = int(request.form.get('chunk_size', 77))
            chunk_overlap = int(request.form.get('chunk_overlap', 1))
            resolution_height = int(request.form.get('resolution_height', 432))
            resolution_width = int(request.form.get('resolution_width', 768))
            seed = int(request.form.get('seed', 42))
            guidance = int(request.form.get('guidance', 7))
        except ValueError as e:
            return jsonify({'error': f'Invalid numeric parameter: {str(e)}'}), 400

        enable_autoregressive = request.form.get('enable_autoregressive') == 'on'

        # Format resolution
        resolution = f"{resolution_height},{resolution_width}"

        # Create settings dict
        settings = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'enable_autoregressive': enable_autoregressive,
            'num_output_frames': num_output_frames,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'resolution': resolution,
            'seed': seed,
            'guidance': guidance
        }

        # Initialize job status
        generation_status[job_id] = {
            'status': 'queued',
            'stage': 'Job queued',
            'created_at': datetime.now().isoformat(),
            'image_file': image_filename,
            'video_file': None,
            'json_config': None,
            'output_lines': [],
            'progress': 0,
            'settings': settings,
            'error': None
        }

        # Start generation in background thread
        thread = threading.Thread(
            target=generate_video_async,
            args=(job_id, image_path, settings)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'job_id': job_id,
            'redirect': f'/status/{job_id}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<job_id>')
@auth.login_required
def status_page(job_id):
    """Status page for a job"""
    if job_id not in generation_status:
        return "Job not found", 404
    return render_template('status.html', job_id=job_id)


@app.route('/api/status/<job_id>')
@auth.login_required
def api_status(job_id):
    """API endpoint for job status"""
    if job_id not in generation_status:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(generation_status[job_id])


@app.route('/preview/<path:filename>')
@auth.login_required
def preview_video(filename):
    """Serve video for preview"""
    return send_from_directory(OUTPUT_FOLDER, filename, mimetype='video/mp4')


@app.route('/download/<path:filename>')
@auth.login_required
def download_file(filename):
    """Download file"""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


@app.route('/uploads/<filename>')
@auth.login_required
def view_upload(filename):
    """View uploaded image"""
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print("=" * 60)
    print("Cosmos Predict 2.5 - Simple Web Interface")
    print("=" * 60)
    print()
    print("Starting server...")
    print()
    print("Local access:   http://127.0.0.1:5000")
    print("Network access: http://<your-local-ip>:5000")
    print()
    print("Username: admin")
    print("Password: cosmos2025")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Run Flask app on all interfaces for network access
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=False,
        threaded=True
    )
