from aravis import Camera
import time
import matplotlib
#from pylab import bar, plot, show, legend, axis, subplot
import matplotlib.pyplot as plt


if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    cam = Camera("AT-Automation Technology GmbH-20805103")
    cam.set_feature("GevSCPSPacketSize", 1500)
    cam.start_acquisition_continuous()
    try:
        start = True
        while True:
            frame = cam.pop_frame()
            plt.clf()
            plt.plot(frame.T)
            if start:
                plt.show(block=False)
                start = False
            else:
                plt.draw()

    finally:
        cam.stop_acquisition()
