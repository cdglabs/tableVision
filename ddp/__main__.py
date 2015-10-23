"""

Usage:

python ddp [-w] [-c CAM_NUM] [-u URL] [-i IMAGE_FILE] PIPELINE

positional arguments:

    PIPELINE: The pipeline to run.

optional arguments:

    -w, --watch: instead of logging to files, this opens a cv2 window that
    shows all the output images. Additionally it watches for changes to the
    source code and reloads the code when something changes. Press SPACE to
    manually reload. Press Q to quit.

    -c CAM_NUM, --camera CAM_NUM: feeds the current webcam image in as the
    input to the pipeline. CAM_NUM is the camera device index.

    -u URL, --url URL: feeds the image at URL in as the input to the pipeline.
    (E.g. for use with the camera server.)

    -i IMAGE_FILE, --image IMAGE_FILE: feeds IMAGE_FILE in as the input to the
    pipeline.


Examples:

    python ddp extract_paper


Notes:

Pipelines may take in any data type as their input. However, when using the
camera, url, or image options, input will be a color cv2 image. So these
options are only suitable for pipelines with color images as their input type.

If no input is given to the pipeline, the pipeline's sample input will be
used.

TODO: command line options...

"""



import sys
import importlib
import infrastructure.log as log
import cv2


# constants
use_live_video = True
run_interactive = True
method_name_to_run = "run"

# variables
frame = None
capture = None
pipeline_name = None


def run_once(module_to_run, log):
    global frame, method_name_to_run, capture
    module_to_run = reload(module_to_run)
    if use_live_video:
        _, frame = capture.read()
    getattr(module_to_run, method_name_to_run)(frame)

    log.finish_log_cycle()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return True  # break


def main():
    global frame, capture, pipeline_name
    assert len(sys.argv) > 1, "First command line argument must be a pipeline name to run"

    pipeline_name = sys.argv[1]
    pipeline = importlib.import_module("pipeline." + pipeline_name)
    assert hasattr(pipeline, method_name_to_run), "module has to have "+method_name_to_run+" method"

    # TODO: Implement logging options besides file output.
    # TODO: Implement webcam, url, and image options.
    log.clear_log_directory()
    log.set_file_prefix(pipeline_name)
    log.set_method("stream")

    if use_live_video:
        capture = cv2.VideoCapture(1)
        # resolution
        capture.set(3, 1920)
        capture.set(4, 1080)
    else:
        frame = pipeline.sample()

    if run_interactive:
        pipeline = reload(pipeline)
        while True:
            if run_once(pipeline, log):
                break

    else:
        run_once(pipeline, log)

    if not run_interactive:
        cv2.waitKey(0)
    if use_live_video:
        capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
