"""
Creates a web server serving the browser-based editor and visualization
environment.
"""

import os, glob, json, subprocess

from flask import Flask, send_from_directory, make_response, request
from functools import update_wrapper

SOURCE_DIR = "../ddp2/"
LOG_DIR = "../log/"

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

@app.route("/log/<path:file_name>")
@nocache
def log_file(file_name):
    return send_from_directory(LOG_DIR, file_name)

# Server -> Browser

@app.route("/sourceFiles.json")
def get_source_files():
    result = []
    file_paths = glob.glob(SOURCE_DIR + "*.py")
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_content = read_file(file_path)
        result.append({
            "fileName": file_name,
            "content": file_content
        })
    return json.dumps(result)

@app.route("/logEntries.json")
def get_log_entries():
    return read_file(LOG_DIR + "data.json")

def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

def write_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)

# Browser -> Server

@app.route("/save", methods=["POST"])
def save_and_run():
    data = request.get_json()
    write_source_files(data["sourceFiles"])
    print "wrote files!"
    result = run_file(data["currentFileName"])
    print "ran file", result
    return "{success: true}"

def write_source_files(source_files):
    for source_file in source_files:
        file_name = source_file["fileName"]
        content = source_file["content"]
        write_file(SOURCE_DIR + file_name, content)

def run_file(file_name):
    return subprocess.call(["python", SOURCE_DIR + file_name])




# Start it

if __name__ == '__main__':
    app.run(debug=True)
