import aravis
import cv2
import time


if __name__ == "__main__":
    ar = aravis.Aravis()
    cam = ar.get_camera("Prosilica-02-2110A-06145")
    #cam = ar.get_camera("AT-Automation Technology GmbH-20805103")
    width, height =  cam.get_sensor_size() 
    cam.set_region(0, 0, width, height)
    x, y, width, height = cam.get_region()
    print("Camera model: ", cam.get_model_name())
    print("Vendor Name: ", cam.get_vendor_name())
    print("Device id: ", cam.get_device_id())
    print("Image size: ", width, ",", height)
    print("Sensor size: ", cam.get_sensor_size()) 
    print("Exposure: ", cam.get_exposure_time())
    print("Frame rate: ", cam.get_frame_rate())
    print("Payload: ", cam.get_payload())
    print("AcquisitionMode: ", cam.get_string_feature("AcquisitionMode"))
    print("Acquisition vals: ", cam.get_enum_vals("AcquisitionMode"))
    print("TriggerSource: ", cam.get_string_feature("TriggerSource"))
    print("TriggerSource vals: ", cam.get_enum_vals("TriggerSource"))
    print("TriggerMode: ", cam.get_string_feature("TriggerMode"))
    print("Bandwidth: ", cam.get_integer_feature("StreamBytesPerSecond"))
    print("PixelFormat: ", cam.get_string_feature("PixelFormat"))
    print("PacketSize: ", cam.get_integer_feature("GevSCPSPacketSize"))
    cam.set_integer_feature("GevSCPSPacketSize", 1500)
    cam.setup_stream()
    cam.start_acquisition_continuous()
    cv2.namedWindow('capture')
    try:
        while True:
            frame = None
            while frame == None:
                frame = cam.try_get_frame()
                time.sleep(0.001)
            print(time.time())
            cv2.imshow("capture", frame)
            cv2.waitKey(1)
    except:
        cam.stop_acquisition()
        cam.cleanup()
        raise

    
