import sys
import time
import cv2
import numpy as np


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("Usage show-npy path/to/npyfile.npy")
        sys.exit(1)
    cv2.namedWindow('capture', flags=0)
    frame = np.load(path)
    cv2.imshow("capture", frame)
    cv2.waitKey(0)
