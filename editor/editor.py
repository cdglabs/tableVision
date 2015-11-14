"""
Creates a web server serving the browser-based editor and visualization
environment.
"""

import os, glob, json

from flask import Flask, send_from_directory

SOURCE_DIR = "../ddp2/"
LOG_BASE_DIR = "../log/"

app = Flask(__name__, static_url_path="")

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
def log_file(file_name):
    log_dirs = [
        log_dir
        for log_dir in glob.glob(LOG_BASE_DIR + "*")
        if os.path.isdir(log_dir)
    ]

    # Take the last one (most recent).
    log_dir = log_dirs[-1]

    return send_from_directory(log_dir, file_name)

def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

if __name__ == '__main__':
    app.run()
