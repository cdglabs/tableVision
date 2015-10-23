# Dependencies

Python libraries to install:

* cv2
* numpy
* scikit-image
* networkx

For camera server:

* gphoto2

(TODO: Make sure this list is complete.)


# Usage

Run a pipeline with, e.g.

    python ddp cv

(TODO: More command line options.)


# Code Organization

`camera_server/`. Code that runs on the computer with the camera. Creates a webserver that anyone can query for the current picture. (TODO)

`ddp/`. The code for doing dynamic drafting paper (ddp).

`ddp/core/`. All the core logic. A bunch of functions for processing images, graphs, etc.

`ddp/infrastructure/`. Code for interfacing with the outside world.

`ddp/pipeline/`. Pipelines of functions for performing particular tasks. Each pipeline module must contain a `run` function which takes an input and returns an output. It should also contain a `sample` function which returns a sample input that can be run through the pipeline (that is, `run(sample())` should work).

`ddp/__main__.py`. This is the "runner" that runs pipelines in various ways.


# Logging

In order to visualize pipeline execution, pipeline `run` functions should make calls to `infrastructure.log`, in particular `infrastructure.log.image(...)`.

By default, logging calls will output files in the `log/` directory. However, this behavior can be changed, e.g. to a live view (TODO).
