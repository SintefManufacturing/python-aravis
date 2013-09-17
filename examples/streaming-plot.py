import sys
from aravis import Camera
import time
import matplotlib
#from pylab import bar, plot, show, legend, axis, subplot
import matplotlib.pyplot as plt


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("None", "null"):
            cam = Camera()
        else:
            cam = Camera(arg)
    else:
        cam = Camera()
    
    #cam.set_feature("GevSCPSPacketSize", 1500)
    cam.start_acquisition_continuous()
    try:
        start = True
        while True:
            frame = cam.pop()
            plt.clf()
            plt.plot(frame.T)
            if start:
                plt.show(block=False)
                start = False
            else:
                plt.draw()

    finally:
        cam.stop_acquisition()
