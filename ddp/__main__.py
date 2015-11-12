import importlib
import infrastructure.log as log
import cv2
from optparse import OptionParser
import infrastructure.streamingClient as streamingClient
import infrastructure.intake as intake
import infrastructure.helper as helper
import signal
import sys
from Settings import Settings
import traceback

def run_once(module_to_run, options, frame, capture):
    module_to_run = reload(module_to_run)
    if options.image_source == "webcamStream":
        _, frame = capture.read()
    try:
        getattr(module_to_run, Settings.METHOD_NAME_TO_RUN)(frame)
    except:
        traceback.print_exc()
        return True
    log.finish_log_cycle()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return True  # break


def main():
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--pipeline", default='full_process', type='string', action="store", dest="pipeline",
        help="any file name from ./pipeline (written without '.py')")
    parser.add_option("--log", default=False, action="store_true", dest="log")
    parser.add_option("--interactive", default=False, action="store_true", dest="interactive")
    parser.add_option("--image_source", default="webcamStill", type='string', action="store", dest="image_source",
        help="webcamStill, webcamStream, sample, webcamStillLocal, webcamStreamLocal")  # TODO add custom file option

    (options, args) = parser.parse_args()

    frame = None
    capture = None
    pipeline_name = options.pipeline
    pipeline = importlib.import_module("pipeline." + pipeline_name)
    assert hasattr(pipeline, Settings.METHOD_NAME_TO_RUN),\
        "module has to have " + Settings.METHOD_NAME_TO_RUN + " method"
    
    # log.clear_log_directory()
    log.set_file_prefix(pipeline_name)

    if options.image_source == "webcamStream":
        options.interactive = True
        capture = streamingClient.connect_to_streaming_server()
    if options.image_source == "webcamStreamLocal":
        options.interactive = True
        capture = helper.get_webcam_capture(1)
    if options.log:
        log.set_method("file")
    if options.interactive:
        log.set_method("stream")
    if options.image_source == "sample":
        frame = pipeline.sample()
    if options.image_source == "webcamStill":
        frame = streamingClient.get_one_picture_from_streaming_server()
    if options.image_source == "webcamStillLocal":
        frame = intake.image_file(helper.take_picture_from_webcam(1))
    
    assert frame is not None or capture is not None
    
    def close(signal=None, frame=None):
        if capture is not None:
            capture.release()
        cv2.destroyAllWindows()
        print "done"
        sys.exit()
    
    signal.signal(signal.SIGINT, close)
    
    if options.interactive:
        # reload only reloads the immediate file, not its dependencies
        pipeline = reload(pipeline)
        while True:
            if run_once(pipeline, options, frame, capture):
                break
    else:
        run_once(pipeline, options, frame, capture)

    close()



if __name__ == "__main__":
    main()

