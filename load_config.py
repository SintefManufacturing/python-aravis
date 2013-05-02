import sys

from aravis import Camera

if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    cam = Camera("AT-Automation Technology GmbH-20805103")
    try:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            print("usage: {} config_file".format(sys.argv[0]))
            sys.exit(1)
        print("loading configuration from ", path) 
        cam.load_config(path)
    finally:
        cam.shutdown()

