Starting from: a raw color image of a piece of paper on a table.

1. Finds edges.

2. Finds the paper by extracting the biggest paper-sized contour.

3. Warps the original image based on the found paper so that the paper is now represented as a 1100x800 pixel image (100dpi).

4. Extracts the ink from the paper using adaptive thresholding.

5. Skeletonizes the ink, resulting in a 1 pixel outline of the sketch.
