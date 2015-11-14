"""
Creates a web server serving the browser-based editor and visualization
environment.
"""

import os, glob, json

from flask import Flask, send_from_directory, make_response
from functools import update_wrapper

SOURCE_DIR = "../ddp2/"
LOG_BASE_DIR = "../log/"

app = Flask(__name__, static_url_path="")


# via https://gist.github.com/roshammar/8932394
def nocache(f):
    def new_func(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        return resp
    return update_wrapper(new_func, f)


# Routes

@app.route("/")
def root():
    return app.send_static_file("index.html")

@app.route("/sourcefiles")
def sourcefiles():
    result = []

    file_paths = glob.glob(SOURCE_DIR + "*.py")
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_content = read_file(file_path)
        result.append({
            "name": file_name,
            "content": file_content
        })

    print result
    return json.dumps(result)

@app.route("/log/<path:file_name>")
@nocache
def log_file(file_name):
    log_dir = get_current_log_dir()
    return send_from_directory(log_dir, file_name)


# Helpers

def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

def get_current_log_dir():
    log_dirs = [
        log_dir
        for log_dir in glob.glob(LOG_BASE_DIR + "*")
        if os.path.isdir(log_dir)
    ]
    # Take the last one (most recent).
    return log_dirs[-1]


# Start it

if __name__ == '__main__':
    app.run()
