import sys
import time
import cv2
from aravis import Camera


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("None", "null"):
            cam = Camera(None)
        elif arg in ("pro", "prosilica"):
            cam = ar.get_camera("Prosilica-02-2130A-06106")
        elif arg in ("at"):
            cam = Camera("AT-Automation Technology GmbH-20805103")
        else:
            cam = Camera(arg)
    else:
        cam = Camera("AT-Automation Technology GmbH-20805103")
    try:
        cam.start_acquisition_continuous()
        cv2.namedWindow('capture', flags=0)

        count = 0
        while True:
            count += 1
            print("frame nb: ", count)
            frame = cam.get_frame(wait=True)
            print(time.time())
            cv2.imshow("capture", frame)
            cv2.waitKey(1)
    finally:
        cam.stop_acquisition()
        cam.shutdown()
