from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import ssl

import json
import os
import uuid
import time
from threading import Lock

# APP

app = Flask(
    __name__,
    static_folder='../frontend',
    static_url_path=''
)

app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)

# PATHS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MESSAGES_FILE = os.path.join(BASE_DIR, 'messages.json')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

FILES_FOLDER = os.path.join(UPLOAD_FOLDER, 'files')
VOICES_FOLDER = os.path.join(UPLOAD_FOLDER, 'voices')

os.makedirs(FILES_FOLDER, exist_ok=True)
os.makedirs(VOICES_FOLDER, exist_ok=True)

# SETTINGS

ALLOWED_FILES = {
    'png',
    'jpg',
    'jpeg',
    'gif',
    'webp',
    'pdf',
    'txt',
    'zip',
    'mp4',
    'mp3'
}

messages_lock = Lock()

# HELPERS

def allowed_file(filename):
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()

    return ext in ALLOWED_FILES


def load_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    return []


def save_messages():
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=2
        )


messages = load_messages()

# ROUTES

@app.route('/')
def index():
    return send_from_directory(
        app.static_folder,
        'index.html'
    )


@app.route('/uploads/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(
        FILES_FOLDER,
        filename
    )


@app.route('/uploads/voices/<path:filename>')
def uploaded_voice(filename):
    return send_from_directory(
        VOICES_FOLDER,
        filename
    )

# SOCKET EVENTS

@socketio.on('connect')
def handle_connect():
    socketio.emit(
        'load_history',
        messages,
        to=request.sid
    )


@socketio.on('send_message')
def handle_message(data):

    text = data.get('text', '').strip()

    if not text:
        return

    if len(text) > 3000:
        return

    message = {
        'id': str(uuid.uuid4()),
        'type': 'text',
        'text': text,
        'timestamp': int(time.time())
    }

    with messages_lock:

        messages.append(message)

        if len(messages) > 1000:
            messages.pop(0)

        save_messages()

    socketio.emit(
        'new_message',
        message
    )

# FILE UPLOAD

@app.route('/upload/file', methods=['POST'])
def upload_file():

    file = request.files.get('file')

    if not file:
        return {
            'error': 'No file'
        }, 400

    filename = secure_filename(file.filename)

    if not filename:
        return {
            'error': 'Invalid filename'
        }, 400

    if not allowed_file(filename):
        return {
            'error': 'File type not allowed'
        }, 400

    ext = os.path.splitext(filename)[1]

    unique_name = f'{uuid.uuid4()}{ext}'

    filepath = os.path.join(
        FILES_FOLDER,
        unique_name
    )

    file.save(filepath)

    message = {
        'id': str(uuid.uuid4()),
        'type': 'file',
        'filename': filename,
        'url': f'/uploads/files/{unique_name}',
        'timestamp': int(time.time())
    }

    with messages_lock:

        messages.append(message)

        if len(messages) > 1000:
            messages.pop(0)

        save_messages()

    socketio.emit(
        'new_message',
        message
    )

    return {
        'success': True
    }

# VOICE UPLOAD

@app.route('/upload/voice', methods=['POST'])
def upload_voice():

    file = request.files.get('voice')

    if not file:
        return {
            'error': 'No voice'
        }, 400

    unique_name = f'{uuid.uuid4()}.webm'

    filepath = os.path.join(
        VOICES_FOLDER,
        unique_name
    )

    file.save(filepath)

    message = {
        'id': str(uuid.uuid4()),
        'type': 'voice',
        'url': f'/uploads/voices/{unique_name}',
        'timestamp': int(time.time())
    }

    with messages_lock:

        messages.append(message)

        if len(messages) > 1000:
            messages.pop(0)

        save_messages()

    socketio.emit(
        'new_message',
        message
    )

    return {
        'success': True
    }

# RUN

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('certificate.crt', 'private.key')
    app.run(
        host='0.0.0.0',
        port=8888,
        ssl_context=context,
        debug=True
    )