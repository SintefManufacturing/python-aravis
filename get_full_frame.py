import time

from aravis import Camera

if __name__ == "__main__":
    try:
        #cam = ar.get_camera("Prosilica-02-2130A-06106")
        cam = Camera("AT-Automation Technology GmbH-20805103")

        print("Camera model: ", cam.get_model_name())
        print("Vendor Name: ", cam.get_vendor_name())
        print("Device id: ", cam.get_device_id())
        print("Region: ", cam.get_region())
        
        #cam.load_config("full_frame_8bit.cxc")
        cam.set_feature("GevSCPSPacketSize", 1500)
        cam.start_acquisition()
        frame = cam.get_frame(wait=True)
        cam.stop_acquisition()
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell(local_ns=locals())
    finally:
        cam.shutdown()

