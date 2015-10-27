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



import importlib
import infrastructure.log as log
import cv2
from optparse import OptionParser
import infrastructure.photoClient as photoClient
import infrastructure.intake as intake
import infrastructure.helper as helper

# constants
method_name_to_run = "run"

# variables
frame = None
capture = None
pipeline_name = None


def run_once(module_to_run, options):
    global frame, method_name_to_run, capture
    module_to_run = reload(module_to_run)
    if options.image_source == "webcamStream":
        _, frame = capture.read()
    getattr(module_to_run, method_name_to_run)(frame)

    log.finish_log_cycle()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return True  # break


def main():
    global frame, capture, pipeline_name
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--pipeline", default='full_process', type='string', action="store", dest="pipeline",
        help="any file name from ./pipeline (written without '.py')")
    parser.add_option("--log", default=False, action="store_true", dest="log")
    parser.add_option("--interactive", default=False, action="store_true", dest="interactive")
    parser.add_option("--image_source", default="newPhoto", type='string', action="store", dest="image_source",
        help="newPhoto, webcamStill, webcamStream, sample")  # TODO add custom file option
    
    (options, args) = parser.parse_args()
    
    pipeline_name = options.pipeline
    pipeline = importlib.import_module("pipeline." + pipeline_name)
    assert hasattr(pipeline, method_name_to_run), "module has to have "+method_name_to_run+" method"
    
    log.clear_log_directory()
    log.set_file_prefix(pipeline_name)
    
    if options.image_source == "webcamStream":
        options.interactive = True
        capture = cv2.VideoCapture(1)
        # resolution
        capture.set(3, 1920)
        capture.set(4, 1080)
        
    if not options.log:
        log.set_method("silent")
    elif options.interactive:
        log.set_method("stream")
    
    if options.image_source == "newPhoto":
        try:
            file = photoClient.get_photo_from_server()
            frame = intake.image_file(file)
        except Exception:
            print "could not get photo. using sample file instead."
            options.image_source = "sample"
            
    if options.image_source == "sample":
        frame = pipeline.sample()
        
    if options.image_source == "webcamStill":
        frame = intake.image_file(helper.take_picture_from_webcam())
        
    assert frame is not None or capture is not None
    if options.interactive:
        # TODO reload only reloads the immediate file, not its dependencies
        pipeline = reload(pipeline)
        while True:
            if run_once(pipeline, options):
                break
    else:
        run_once(pipeline, options)
    
    if not options.interactive and options.log:
        cv2.waitKey(0)
    if options.image_source == "webcamStream":
        capture.release()
    cv2.destroyAllWindows()
    print "done"


if __name__ == "__main__":
    main()

