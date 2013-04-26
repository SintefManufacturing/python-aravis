import aravis
import cv2
import time


if __name__ == "__main__":
    ar = aravis.Aravis()
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    cam = ar.get_camera("AT-Automation Technology GmbH-20805103")
    x, y, width, height = cam.get_region()
    print("Camera model: ", cam.get_model_name())
    print("Vendor Name: ", cam.get_vendor_name())
    print("Device id: ", cam.get_device_id())
    print("Image size: ", width, ",", height)
    sensor =  cam.get_sensor_size() 
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
    cam.set_integer_feature("AoiHeight", 2048)
    cam.set_string_feature("CameraMode", "Image")
    cam.set_string_feature("PixelFormat", "Mono8")
    cam.set_integer_feature("GevSCPSPacketSize", 1500)
    cam.set_frame_rate(20)
    cam.setup_stream()
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
        cam.cleanup()
