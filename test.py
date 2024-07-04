from flask import Flask, request, send_file, abort
import os
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Path to the file you want to share
FILE_PATH = 'requirements.txt'

# Token expiration time in seconds (1 hour by default)
TOKEN_EXPIRATION = 3600

# Dictionary to store active tokens (token: expiry_time)
active_tokens = {}


def generate_token():
    token = secrets.token_urlsafe(16)
    expiry_time = datetime.now() + timedelta(seconds=TOKEN_EXPIRATION)
    active_tokens[token] = expiry_time
    return token


def is_token_valid(token):
    current_time = datetime.now()
    if token in active_tokens:
        expiry_time = active_tokens[token]
        if current_time <= expiry_time:
            return True
        else:
            del active_tokens[token]
    return False


@app.route('/generate-download-link', methods=['GET'])
def generate_download_link():
    token = generate_token()
    download_link = f"{request.url_root}download?token={token}"
    return download_link


@app.route('/download', methods=['GET'])
def download_file():
    token = request.args.get('token')
    if not token or not is_token_valid(token):
        abort(404)

    return send_file(FILE_PATH, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
