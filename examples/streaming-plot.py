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
            frame = cam.get_frame(wait=True)
            print(frame.shape)
            plt.clf()
            plt.plot(frame.T)
            if start:
                print("showing")
                plt.show(block=False)
                start = False
            else:
                plt.draw()

        #from IPython.frontend.terminal.embed import InteractiveShellEmbed
        #ipshell = InteractiveShellEmbed( banner1="\nStarting IPython shell, robot object is available\n")
        #ipshell(local_ns=locals())
    finally:
        cam.stop_acquisition()
        cam.shutdown()
