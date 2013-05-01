import time
import cv2
from aravis import Camera


if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    #cam = Camera("AT-Automation Technology GmbH-20805103")
    cam = Camera(None)
    cam.set_feature("GevSCPSPacketSize", 1500)
    cam.set_frame_rate(20)
    cam.create_buffers(20)
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
