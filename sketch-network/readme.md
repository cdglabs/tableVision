Starting from: a skeletonized image (white on black) of a sketch.

1. Creates a networkx graph of the skeletonized image. Every white pixel becomes a node and there is an edge between any neighboring pixels, using the 8-neighborhood of a pixel.

2. Simplifies junctures. A juncture is a node with more than 2 or less than 2 neighbors. There are often clusters of junctures where lines in the sketch meet. By simplifying junctures, we find any clumps of junctures that are within e.g. 5 pixel distance. Then we "bomb" all the pixels within this 5 pixel radius. We replace the clump of junctures with a single juncture node, and connect edges appropriately to the rest of the drawing.

3. Simplifies paths. A path is a series of nodes between junctures. We simplify using the [RDP Algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm) for simplifying curves. This eliminates nodes in such a way that the simplified path remains within e.g. 3 pixels of the original path.

4. Straighten lines. (This won't be used for curves.) This finds any "corners" whose angle is less than e.g. .1 of pi and eliminates those nodes.
