import sys
import aravis
import cv2
import time


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "frame.png"
    #cam = aravis.Camera("AT-Automation Technology GmbH-20805103")
    cam = aravis.Camera()
    cam.start_acquisition_continuous()
    try:
        frame = None
        while frame == None:
            frame = cam.get_frame(wait=True)
        print("Saving image to ", path)
        cv2.imwrite(path, frame)
    finally:
        cam.stop_acquisition()
        cam.cleanup()
