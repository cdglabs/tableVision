# Dynamic Drafting Paper

![Horizontal/Vertical Lines Test](doc/hv_lines.jpg)

Dynamic Drafting Paper is an experimental system for doing CAD without screens. We're particularly interested in how group dynamics around computation will change without screens.


# Usage

All the core algorithms are in the folder `/ddp2` (TODO: replace with ddp). These files can be run in Python and they will log their results to the `/log` folder.

## Editor

To use the integrated editor, run:

    python editor/editor.py

This will start up a web server. Access the editor in the browser at:

    http://localhost:5000/

The editor will display logged images directly within the code.

TODO: Screenshot here.

To save, press Cmd+S. This will save changes to all files and execute the currently editing file, refreshing log images when execution completes.


# Dependencies

Python libraries to install:

* cv2
* numpy
* scikit-image
* networkx
* cairosvg
    * cairo: brew install cairo

For printing:

* lpr

For camera server:

* gphoto2
* websocket-client

(TODO: Make sure this list is complete.)
