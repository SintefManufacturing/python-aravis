import sys
import time
import cv2
from aravis import Camera


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("None", "null"):
            cam = Camera(None)
        else:
            cam = Camera(arg)
    else:
        cam = Camera()

    try:
        cam.start_acquisition_continuous()
        cv2.namedWindow('capture', flags=0)

        count = 0
        while True:
            count += 1
            print("frame nb: ", count)
            frame = cam.pop_frame()
            print("shape: ", frame.shape)
            print(time.time())
            if not 0 in frame.shape:
                cv2.imshow("capture", frame)
                cv2.waitKey(1)
    finally:
        cam.stop_acquisition()
