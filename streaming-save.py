import sys
import time
import numpy as np
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
        cam.set_feature("GevSCPSPacketSize", 1500)
        cam.set_frame_rate(20)
        cam.start_acquisition_continuous()

        count = 0
        lastcount = 0
        lasttid = time.time()
        while True:
            count += 1
            frame = cam.get_frame(wait=True)
            tid = time.time()
            np.save(str(tid) + ".npy", frame)
            print("frame nb: ", count)
            if count - lastcount >= 10:
                lastcount = count
                print("Frame rate: ", 10/(tid - lasttid))
                lasttid = tid
    finally:
        cam.stop_acquisition()
        cam.shutdown()
