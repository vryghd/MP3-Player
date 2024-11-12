from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Specify the full path to the Python executable in your virtual environment
PYTHON_PATH = os.path.join("C:\\Users\\chris\\Desktop\\MP3 Player\\venv\\Scripts\\python.exe")

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Run download_audio.py with the YouTube URL and capture output
        result = subprocess.run(
            [PYTHON_PATH, 'download_audio.py', youtube_url],
            check=True,
            capture_output=True,
            text=True,
            cwd="C:\\Users\\chris\\Desktop\\MP3 Player"  # Ensure the correct working directory
        )
        
        # Log the subprocess output for debugging
        print("Subprocess output:", result.stdout)
        print("Subprocess error (if any):", result.stderr)
        
        return jsonify({'message': 'Download initiated successfully!'})
    except subprocess.CalledProcessError as e:
        # Log the error details if the subprocess fails
        print("Error in subprocess:", e.stderr)
        return jsonify({'error': f"Subprocess error: {e.stderr}"}), 500
    except Exception as e:
        # Log any other exceptions
        print("General error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
