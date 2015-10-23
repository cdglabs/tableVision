import sys
import importlib
import infrastructure.log as log


assert len(sys.argv) > 1, "First command line argument must be a pipeline name to run"

pipeline_name = sys.argv[1]
pipeline = importlib.import_module("pipeline." + pipeline_name)

# If no input is specified, use the pipeline's sample input. TODO: Should be
# able to specify input as second command line argument.
pipeline_input = pipeline.sample()


log.clear_log_directory()
log.set_file_prefix(pipeline_name)
pipeline.run(pipeline_input)
