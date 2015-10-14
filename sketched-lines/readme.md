This starts from the assumption that we've extracted the sheet of paper and now we need to find the sketched lines.

threshold.py shows how to apply an adaptive threshold to separate ink from paper. The parameters might need tuning but overall this approach is good.

corner.py shows how to detect corners, using OpenCV's goodFeaturesToTrack function. This works, but the parameters seem finicky and I don't like how black box the algorithm is. I think we should try to replace this stage with something morphological (find T's etc in the skeletonization of the sketch), and then find corners by looking for them globally, not locally.

connected.py shows how to analyze the topology of the drawing to connect the corners. It draws black circles at the corners to turn the drawing into "bridges". Then I findContours on these bridges and use them to determine which corners are connected to which other corners.

constraints.py separates lines into horizontal or vertical and then solves the constraints. This will be replaced with a much richer constraint solver (akin to Sketchpad), but this works for now with these two hardcoded constraints.
