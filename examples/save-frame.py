import sys
import numpy as np
from aravis import Camera


if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    #cam = Camera("AT-Automation Technology GmbH-20805103")
    cam = Camera()
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "frame.npy"

    #cam.start_acquisition_trigger()
    cam.start_acquisition_continuous()
    frame = cam.pop()
    print("Saving frame to ", path)
    np.save(path, frame)
    cam.stop_acquisition()
