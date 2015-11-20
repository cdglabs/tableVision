"""
These are functions that log images into the log directory.

Usage examples:

    log.image(img)

    log.image_hsv(background_img,
        log.contours(contours, color=(0,255,0)),
        log.points(points)
    )

The first time a log function is called, the log directory will be cleared.

Every call to log will write a new image file and also write an entry to
data.json. This JSON file contains a list of {file, line, image} entries.
"""

import os, glob, traceback, json
import cv2

def image(img, *overlays):
    """Log a BGR image, optionally with overlays.

    Overlays are functions that take the image and draw on top of it (mutating
    it).
    """
    # Ensure we don't mutate img.
    img = img.copy()
    # Apply overlays.
    for overlay in overlays:
        overlay(img)
    write_log_entry(img)

def image_grey(img, *overlays):
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    image(img, *overlays)

def image_hsv(img, *overlays):
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    image(img, *overlays)


# =============================================================================
# Overlays
# =============================================================================

def contours(cs, color=(0,0,255), thickness=2):
    def overlay(img):
        cv2.drawContours(img, cs, -1, color, thickness)
    return overlay

def points(ps, color=(0,0,255), radius=3):
    def overlay(img):
        for (x,y) in ps:
            cv2.circle(img, (int(x),int(y)), radius, color, -1)
    return overlay

def pixels(ps, color=(0,0,255)):
    def overlay(img):
        for (x,y) in ps:
            img[int(y),int(x)] = color
    return overlay

# TODO: lines, circles, other overlays you might want to draw...


# =============================================================================
# Logging Internals
# =============================================================================

log_dir = "../log/"
log_entries = []

def initialize_log_directory():
    # Clear files in log directory.
    files = glob.glob(log_dir + "*")
    for f in files:
        if not os.path.isdir(f):
            os.remove(f)

    # Reset log entries.
    del log_entries[:]
    update_log_data()

def write_log_entry(img):
    # Generate image file name.
    out_count = len(log_entries)
    image_file_name = str(out_count).rjust(3, "0") + ".png"
    image_path = log_dir + image_file_name

    # Write image file.
    cv2.imwrite(image_path, img)

    # Figure out who called log.
    (caller_file, caller_line) = get_caller()

    # Add entry to log_entries.
    entry = {
        "fileName": caller_file,
        "lineNumber": caller_line,
        "image": image_file_name
    }
    log_entries.append(entry)

    # Update log data file.
    update_log_data()

def get_caller():
    tb = traceback.extract_stack()

    # Convert all file paths to relative paths. TODO: This currently just
    # assumes everything is in the same directory, so it needs fixing if we
    # start having multiple directories of python files.
    tb = [
        (os.path.basename(file_name), line, function_name, code)
        for (file_name, line, function_name, code) in tb
    ]

    # Remove all entries that are within our file (log.py).
    tb = [
        (file_name, line, function_name, code)
        for (file_name, line, function_name, code) in tb
        if file_name != "log.py"
    ]

    # The caller is the last entry in tb
    (file_name, line, function_name, code) = tb[-1]

    return (file_name, line)

def update_log_data():
    # Encode as JSON, prettified.
    json_string = json.dumps(log_entries, indent=2)

    with open(log_dir + "data.json", "w") as json_file:
        json_file.write(json_string)

# Initialize log directory when this module starts up.
initialize_log_directory()
