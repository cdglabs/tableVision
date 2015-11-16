"""
Creates a web server serving the browser-based editor and visualization
environment.
"""

import os, glob, json

from flask import Flask, send_from_directory, make_response
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
    return send_from_directory(LOG_DIR, file_name)

@app.route("/run/<path:file_name>")
def run_file(file_name):
    "TODO"

@app.route("/save/<path:file_name>")
def save_file(file_name):
    "TODO"
    # Needs to access request data, maybe should be a POST method
    # http://flask.pocoo.org/docs/0.10/quickstart/#accessing-request-data


# Helpers

def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


# Start it

if __name__ == '__main__':
    app.run(debug=True)
