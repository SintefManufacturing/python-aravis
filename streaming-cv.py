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

    cam.set_feature("GevSCPSPacketSize", 1500)
    cam.set_frame_rate(20)
    cam.create_buffers()
    cam.start_acquisition_continuous()
    cv2.namedWindow('capture')

    count = 0
    try:
        while True:
            count += 1
            print("frame nb: ", count)
            frame = None
            while frame == None:
                frame = cam.try_get_frame()
                time.sleep(0.001)
            print(time.time())
            cv2.imshow("capture", frame)
            cv2.waitKey(1)
    finally:
        cam.stop_acquisition()
