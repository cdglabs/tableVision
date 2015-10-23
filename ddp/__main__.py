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


assert len(sys.argv) > 1, "First command line argument must be a pipeline name to run"

pipeline_name = sys.argv[1]
pipeline = importlib.import_module("pipeline." + pipeline_name)

# TODO: Implement webcam, url, and image options.
pipeline_input = pipeline.sample()

# TODO: Implement logging options besides file output.
log.clear_log_directory()
log.set_file_prefix(pipeline_name)
pipeline.run(pipeline_input)
