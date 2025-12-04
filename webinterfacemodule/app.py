from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
import subprocess
import threading
import time
from datetime import datetime
import uuid
import re
import json
from pathlib import Path
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'cosmos-predict-gui-secret-key'
auth = HTTPBasicAuth()

# ==================== AUTHENTICATION CONFIGURATION ====================
AUTH_ENABLED = False
AUTH_USERNAME = 'admin'
AUTH_PASSWORD = 'cosmos2025'  # ⚠️ CHANGE THIS PASSWORD!
# =====================================================================

users = {AUTH_USERNAME: generate_password_hash(AUTH_PASSWORD)}

@auth.verify_password
def verify_password(username, password):
    if not AUTH_ENABLED:
        return True
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
QWEN_DIR = PROJECT_ROOT / 'Qwen_instructor_7B'

# ==================== MODE CONFIGURATIONS ====================
# Mode 2: Embodiment-specific AI extension
EMBODIMENT_MODES = {
    'so1': {
        'name': 'SO-1 Arm (LeRobot)',
        'script': 'prompt_extender_so1_arm.py',
        'description': 'Single-arm manipulation from LeRobot',
        'icon': '🦾'
    },
    '2wheel': {
        'name': '2-Wheel Mobile Robot',
        'script': 'prompt_extender_2wheel_mobile.py',
        'description': 'Differential drive navigation',
        'icon': '🤖'
    },
    'bimanual': {
        'name': 'Bimanual UR3',
        'script': 'prompt_extender_bimanual_ur3.py',
        'description': 'Dual-arm coordination',
        'icon': '🤝'
    }
}

# Mode 3: General analyzer
GENERAL_MODE = {
    'name': 'General Image Analyzer',
    'script': 'prompt_extender_general.py',
    'description': 'AI analyzes any robot/scene',
    'icon': '🔬'
}
# ==============================================================

# Global status tracking
generation_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_form_int(form, key, default):
    """Safely get integer from form, handling empty strings"""
    value = form.get(key, '')
    if value == '' or value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def get_form_float(form, key, default):
    """Safely get float from form, handling empty strings"""
    value = form.get(key, '')
    if value == '' or value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def run_mode1_manual(job_id, image_path, prompt, negative_prompt, **kwargs):
    """Mode 1: Manual - No AI extension"""
    try:
        generation_status[job_id]['stage'] = 'Manual mode - creating config...'

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_base = f"manual_{timestamp}"
        output_txt = str(Path(OUTPUT_FOLDER) / f"{output_base}_prompt.txt")
        json_file = output_txt.replace('.txt', '.json')

        # Save prompt
        with open(output_txt, 'w') as f:
            f.write(prompt)

        # Create JSON config (correct Cosmos format)
        cosmos_data = {
            "name": output_base,
            "input_path": os.path.abspath(image_path),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_output_frames": kwargs.get('frames', 77),
            "resolution": f"{kwargs.get('height', 432)},{kwargs.get('width', 768)}",
            "seed": kwargs.get('seed', 42),
            "guidance": int(kwargs.get('guidance', 7.0)),
            "inference_type": "image2world"
        }

        with open(json_file, 'w') as f:
            json.dump(cosmos_data, f, indent=2)

        generation_status[job_id]['prompt_file'] = os.path.basename(output_txt)
        generation_status[job_id]['json_file'] = os.path.basename(json_file)
        generation_status[job_id]['output_lines'].append("✓ Manual mode: Config created")

        # Store prompts and settings for display
        generation_status[job_id]['user_prompt'] = prompt
        generation_status[job_id]['extended_prompt'] = prompt  # Same in manual mode
        generation_status[job_id]['negative_prompt'] = negative_prompt
        generation_status[job_id]['settings'] = {
            'frames': kwargs.get('frames', 77),
            'resolution': f"{kwargs.get('width', 768)}x{kwargs.get('height', 432)}",
            'seed': kwargs.get('seed', 42),
            'guidance': kwargs.get('guidance', 7.0),
            'mode': 'Manual Control'
        }

        return json_file

    except Exception as e:
        raise Exception(f"Manual mode failed: {e}")

def run_mode2_embodiment(job_id, embodiment_type, image_path, prompt, max_tokens=600):
    """Mode 2: Embodiment-specific AI extension"""
    try:
        generation_status[job_id]['stage'] = f'Analyzing with {EMBODIMENT_MODES[embodiment_type]["name"]}...'

        script_name = EMBODIMENT_MODES[embodiment_type]['script']
        script_path = QWEN_DIR / script_name

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_base = f"{embodiment_type}_{timestamp}"
        output_txt = str(Path(OUTPUT_FOLDER) / f"{output_base}_prompt.txt")

        cmd = [
            'python3', str(script_path),
            '--image', image_path,
            '--prompt', prompt,
            '--output', output_txt,
            '--max-tokens', str(max_tokens)
        ]

        generation_status[job_id]['output_lines'].append(f"Running: {' '.join(cmd)}")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        for line in process.stdout:
            generation_status[job_id]['output_lines'].append(line.strip())

        process.wait()

        if process.returncode != 0:
            raise Exception(f"Embodiment extender failed with code {process.returncode}")

        json_file = output_txt.replace('.txt', '.json')
        if not os.path.exists(json_file):
            raise Exception(f"JSON file not created: {json_file}")

        # Read extended prompt and JSON config
        with open(output_txt, 'r', encoding='utf-8') as f:
            extended_prompt = f.read()

        with open(json_file, 'r') as f:
            config = json.load(f)

        generation_status[job_id]['prompt_file'] = os.path.basename(output_txt)
        generation_status[job_id]['json_file'] = os.path.basename(json_file)

        # Store prompts and settings for display
        generation_status[job_id]['user_prompt'] = prompt
        generation_status[job_id]['extended_prompt'] = extended_prompt
        generation_status[job_id]['negative_prompt'] = config.get('negative_prompt', 'N/A')

        # Parse resolution from new format "height,width"
        resolution_str = config.get('resolution', '432,768')
        if ',' in resolution_str:
            h, w = resolution_str.split(',')
            resolution_display = f"{w.strip()}x{h.strip()}"
        else:
            resolution_display = resolution_str

        generation_status[job_id]['settings'] = {
            'frames': config.get('num_output_frames', 77),
            'resolution': resolution_display,
            'seed': config.get('seed', 42),
            'guidance': config.get('guidance', 7.0),
            'mode': f"Embodiment - {EMBODIMENT_MODES[embodiment_type]['name']}",
            'max_tokens': max_tokens
        }

        return json_file

    except Exception as e:
        raise Exception(f"Embodiment mode failed: {e}")

def run_mode3_general(job_id, image_path, prompt, max_tokens=700):
    """Mode 3: General image analyzer"""
    try:
        generation_status[job_id]['stage'] = 'Analyzing with General Image Analyzer...'

        script_path = QWEN_DIR / GENERAL_MODE['script']

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_base = f"general_{timestamp}"
        output_txt = str(Path(OUTPUT_FOLDER) / f"{output_base}_prompt.txt")

        cmd = [
            'python3', str(script_path),
            '--image', image_path,
            '--prompt', prompt,
            '--output', output_txt,
            '--max-tokens', str(max_tokens)
        ]

        generation_status[job_id]['output_lines'].append(f"Running: {' '.join(cmd)}")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        for line in process.stdout:
            generation_status[job_id]['output_lines'].append(line.strip())

        process.wait()

        if process.returncode != 0:
            raise Exception(f"General analyzer failed with code {process.returncode}")

        json_file = output_txt.replace('.txt', '.json')
        if not os.path.exists(json_file):
            raise Exception(f"JSON file not created: {json_file}")

        # Read extended prompt and JSON config
        with open(output_txt, 'r', encoding='utf-8') as f:
            extended_prompt = f.read()

        with open(json_file, 'r') as f:
            config = json.load(f)

        generation_status[job_id]['prompt_file'] = os.path.basename(output_txt)
        generation_status[job_id]['json_file'] = os.path.basename(json_file)

        # Store prompts and settings for display
        generation_status[job_id]['user_prompt'] = prompt
        generation_status[job_id]['extended_prompt'] = extended_prompt
        generation_status[job_id]['negative_prompt'] = config.get('negative_prompt', 'N/A')

        # Parse resolution from new format "height,width"
        resolution_str = config.get('resolution', '432,768')
        if ',' in resolution_str:
            h, w = resolution_str.split(',')
            resolution_display = f"{w.strip()}x{h.strip()}"
        else:
            resolution_display = resolution_str

        generation_status[job_id]['settings'] = {
            'frames': config.get('num_output_frames', 77),
            'resolution': resolution_display,
            'seed': config.get('seed', 42),
            'guidance': config.get('guidance', 7.0),
            'mode': 'General Analyzer',
            'max_tokens': max_tokens
        }

        return json_file

    except Exception as e:
        raise Exception(f"General mode failed: {e}")

def run_cosmos_inference(job_id, json_config_path, output_name):
    """Run Cosmos Predict inference"""
    try:
        generation_status[job_id]['status'] = 'generating_video'
        generation_status[job_id]['stage'] = 'Running Cosmos Predict 2.5...'

        output_path = OUTPUT_FOLDER

        cmd = [
            'python3',
            str(PROJECT_ROOT / 'examples' / 'inference.py'),
            '-i', json_config_path,
            '-o', output_path,
            '--disable-guardrails'  # Required for robotics prompts
        ]

        generation_status[job_id]['output_lines'].append(f"\nRunning Cosmos: {' '.join(cmd)}")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        for line in process.stdout:
            generation_status[job_id]['output_lines'].append(line.strip())

        process.wait()

        if process.returncode != 0:
            raise Exception(f"Cosmos inference failed with code {process.returncode}")

        # Find generated video - read the name from the JSON config
        with open(json_config_path, 'r') as f:
            config = json.load(f)
        video_name = config['name']
        video_file = f"{video_name}.mp4"
        video_path = Path(output_path) / video_file
        if not video_path.exists():
            raise Exception(f"Video file not generated: {video_path}")
        generation_status[job_id]['video_file'] = video_file

        return video_file

    except Exception as e:
        raise Exception(f"Cosmos inference failed: {e}")

def generate_video_async(job_id, mode, image_path, prompt, **kwargs):
    """Async video generation for all 3 modes"""
    try:
        generation_status[job_id]['status'] = 'starting'
        generation_status[job_id]['output_lines'] = []

        # Run appropriate mode
        if mode == 'manual':
            negative_prompt = kwargs.pop('negative_prompt', '')
            json_file = run_mode1_manual(job_id, image_path, prompt,
                                        negative_prompt, **kwargs)
        elif mode == 'embodiment':
            json_file = run_mode2_embodiment(job_id, kwargs['embodiment_type'],
                                            image_path, prompt, kwargs.get('max_tokens', 600))
        elif mode == 'general':
            json_file = run_mode3_general(job_id, image_path, prompt,
                                         kwargs.get('max_tokens', 700))
        else:
            raise Exception(f"Unknown mode: {mode}")

        # Update JSON with advanced settings if provided (use correct Cosmos format)
        with open(json_file, 'r') as f:
            config = json.load(f)

        if 'frames' in kwargs:
            config['num_output_frames'] = kwargs['frames']
        if 'height' in kwargs and 'width' in kwargs:
            config['resolution'] = f"{kwargs['height']},{kwargs['width']}"
        if 'seed' in kwargs:
            config['seed'] = kwargs['seed']
        if 'guidance' in kwargs:
            config['guidance'] = int(kwargs['guidance'])

        with open(json_file, 'w') as f:
            json.dump(config, f, indent=2)

        # Run Cosmos inference
        output_name = Path(json_file).stem
        video_file = run_cosmos_inference(job_id, json_file, output_name)

        generation_status[job_id]['status'] = 'completed'
        generation_status[job_id]['stage'] = 'Complete!'

    except Exception as e:
        generation_status[job_id]['status'] = 'failed'
        generation_status[job_id]['error'] = str(e)
        generation_status[job_id]['output_lines'].append(f"\n❌ Error: {e}")

@app.route('/')
@auth.login_required
def index():
    """Main page"""
    # Pass as robot_modes for template compatibility
    return render_template('index.html',
                         robot_modes=EMBODIMENT_MODES,
                         embodiment_modes=EMBODIMENT_MODES,
                         general_mode=GENERAL_MODE)

@app.route('/generate', methods=['POST'])
@auth.login_required
def generate():
    """Handle generation request"""
    try:
        mode = request.form.get('mode')  # manual, embodiment, general
        prompt = request.form.get('prompt')

        if not prompt:
            flash('Please provide a prompt', 'error')
            return redirect(url_for('index'))

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = f"{uuid.uuid4().hex}_{file.filename}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)

        if not image_path:
            flash('Please upload an image', 'error')
            return redirect(url_for('index'))

        # Create job
        job_id = str(uuid.uuid4())
        generation_status[job_id] = {
            'status': 'queued',
            'stage': 'Initializing...',
            'created_at': datetime.now().isoformat()
        }

        # Collect parameters
        kwargs = {}

        if mode == 'manual':
            kwargs['negative_prompt'] = request.form.get('negative_prompt', '')
            kwargs['frames'] = get_form_int(request.form, 'frames', 77)

            # Safe resolution parsing
            res_str = request.form.get('resolution', '768x432')
            if 'x' in res_str:
                res = res_str.split('x')
            elif ',' in res_str:
                res = res_str.split(',')
            else:
                res = ['768', '432']  # default

            try:
                kwargs['width'] = int(res[0].strip())
                kwargs['height'] = int(res[1].strip())
            except (ValueError, IndexError):
                kwargs['width'] = 768
                kwargs['height'] = 432

            kwargs['seed'] = get_form_int(request.form, 'seed', 42)
            kwargs['guidance'] = get_form_float(request.form, 'guidance', 7.0)

        elif mode == 'embodiment':
            kwargs['embodiment_type'] = request.form.get('embodiment_type')
            kwargs['max_tokens'] = get_form_int(request.form, 'max_tokens', 600)
            kwargs['frames'] = get_form_int(request.form, 'frames', 77)
            kwargs['seed'] = get_form_int(request.form, 'seed', 42)
            kwargs['guidance'] = get_form_float(request.form, 'guidance', 7.0)

        elif mode == 'general':
            kwargs['max_tokens'] = get_form_int(request.form, 'max_tokens', 700)
            kwargs['frames'] = get_form_int(request.form, 'frames', 77)
            kwargs['seed'] = get_form_int(request.form, 'seed', 42)
            kwargs['guidance'] = get_form_float(request.form, 'guidance', 7.0)

        # Start async generation
        thread = threading.Thread(
            target=generate_video_async,
            args=(job_id, mode, image_path, prompt),
            kwargs=kwargs
        )
        thread.start()

        return redirect(url_for('status', job_id=job_id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/status/<job_id>')
@auth.login_required
def status(job_id):
    """Status tracking page"""
    if job_id not in generation_status:
        flash('Job not found', 'error')
        return redirect(url_for('index'))

    return render_template('status.html', job_id=job_id, job=generation_status[job_id])

@app.route('/api/status/<job_id>')
@auth.login_required
def api_status(job_id):
    """API endpoint for status"""
    if job_id not in generation_status:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(generation_status[job_id])

@app.route('/outputs/<path:filename>')
@auth.login_required
def download_file(filename):
    """Download generated files"""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/preview/<path:filename>')
@auth.login_required
def preview_video(filename):
    """Preview video"""
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("="*80)
    print("🎬 Cosmos Predict 2.5 Web Interface")
    print("="*80)
    print(f"Authentication: {'Enabled' if AUTH_ENABLED else 'Disabled'}")
    if AUTH_ENABLED:
        print(f"Username: {AUTH_USERNAME}")
        print(f"Password: {AUTH_PASSWORD}")
        print("⚠️  CHANGE THE PASSWORD FOR SECURITY!")
    print("="*80)
    print("Starting server on http://0.0.0.0:5000")
    print("="*80)

    app.run(host='0.0.0.0', port=5000, debug=True)
