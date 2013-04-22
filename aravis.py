from gi.repository import Aravis

class AravisException(Exception):
    pass

class Camera():
    def __init__(self, name):
        self.name = name
        self.cam = Aravis.Camera.new(name)
        self.dev = self.cam.get_device()
        self.stream = self.cam.create_stream(None, None)

    def __getattr__(self, name):
        if hasattr(self.cam, name):
            return getattr(self.cam, name)
        #elif hasattr(self.dev, name):
        #    return getattr(self.dev, name)
        else:
            raise AttributeError

    def __dir__(self):
        tmp = list(self.__dict__.keys()) + self.cam.__dir__()# + self.dev.__dir__()
        return tmp

    def load_config(self, path):
        f = open(path)
        for line in f:
            name, val = line.split()
            name = name.strip()
            val = val.strip()
            self.set_feature(name, val)
        f.close()

    def get_feature_type(self, name):
        genicam = self.dev.get_genicam()
        node = genicam.get_node(name)
        if not node:
            raise AravisException("Feature {} does not seem tp exist in camera".format(name))
        return node.get_node_name()

    def get_feature(self, name):
        ntype = self.get_feature_type(name)
        if ntype in ("Enumeration", "String"):
            return self.dev.get_string_feature_value(name)
        elif ntype == "Integer":
            return self.dev.get_integer_feature_value(name)
        elif ntype == "Float":
            return self.dev.get_float_feature_value(name)
        else:
            print("Feature type not implemented: ", ntype)

    def set_feature(self, name, val):
        ntype = self.get_feature_type(name)
        if ntype in ( "String", "Enumeration"):
            return self.dev.set_string_feature_value(name, val)
        elif ntype == "Integer":
            return self.dev.set_integer_feature_value(name, val)
        elif ntype == "Float":
            return self.dev.set_float_feature_value(name, val)
        else:
            print("Feature type not implemented: ", ntype)


    def get_feature_vals(self, name):
        """
        if feature is an enumeration then return possible values
        """
        ntype = self.get_feature_type(name)
        if ntype == "Enumeration":
            return cam.dev.get_available_enumeration_feature_values_as_strings(name)
        else:
            raise AravisException("{} is not an enumeration but a {}".format(name, ntype))

    def read_register(self, address):
        return self.dev.read_register(address)

    def write_register(self, address, val):
        return self.dev.write_register(address, val)

    def setup_buffers(self, nb):
        payload = self.cam.get_payload()
        for i in range(0, nb):
	        self.stream.push_buffer(Aravis.Buffer.new(payload, None))

    def try_get_frame(self):
        """
        return last frame. Wait if no frame available
        """
        return self.stream.try_pop_array()

    def get_frame(self):
        """
        return last frame. Wait if no frame available
        """
        return self.stream.pop_array()


    def _array_from_buffer(self, buf):
        if not buf:
            return None
        #im = np.ctypeslib.as_array(buf.contents.data, (buf.contents.height, buf.contents.width))
        b = self._buf_from_memory(buf.contents.data, buf.contents.size*8)
        if self.pixel_format == "Mono16":
            pixelformat = np.uint16
        else:
            pixelformat = np.uint8
        im = np.frombuffer(b, dtype=pixelformat, count=buf.contents.height * buf.contents.width)
        im.shape = (buf.contents.width, buf.contents.height) 
        im = im.copy()
        self.push_buffer(buf)
        return im




    def trigger(self):
        """
        trigger camera to take a picture in trigger source mode
        """
        self.execute_command("TriggerSoftware")

    def __str__(self):
        return "Camera: " + self.name

    def __repr__(self):
        return self.__str__()
    
    def start_acquisition(self):
        self.stream.pixel_format = self.get_string_feature("PixelFormat") #FIXME: should read the aravis cache, if possible
        self._ar.dll.arv_camera_start_acquisition(self._handle)

    def start_acquisition_trigger(self):
        self.set_string_feature("AcquisitionMode", "Continuous") #no acquisition limits
        self.set_string_feature("TriggerSource", "Software") #wait for trigger t acquire image
        self.set_string_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition()

    def start_acquisition_continuous(self):
        self.set_string_feature("AcquisitionMode", "Continuous") #no acquisition limits
        self.set_string_feature("TriggerSource", "Freerun") #as fast as possible
        #self.set_string_feature("TriggerSource", "FixedRate") 
        self.set_string_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition()


    def stop_acquisition(self):
        self._ar.dll.arv_camera_stop_acquisition(self._handle)





def get_device_ids():
    n = Aravis.get_n_devices()
    l = [Aravis.get_device_id(i) for i in range(0, n)]
    return l






if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    cam = Camera("AT-Automation Technology GmbH-20805103")
    #x, y, width, height = cam.get_region()
    print("Camera model: ", cam.get_model_name())
    print("Vendor Name: ", cam.get_vendor_name())
    print("Device id: ", cam.get_device_id())
    #print("Image size: ", width, ",", height)
    print("Sensor size: ", cam.get_sensor_size()) 
    print("Exposure: ", cam.get_exposure_time())
    print("Frame rate: ", cam.get_frame_rate())
    print("Payload: ", cam.get_payload())
    print("AcquisitionMode: ", cam.get_feature("AcquisitionMode"))
    print("Acquisition vals: ", cam.get_feature_vals("AcquisitionMode"))
    #print("TriggerMode: ", cam.get_feature("TriggerMode"))
    #print("Bandwidth: ", cam.get_feature("StreamBytesPerSecond"))
    print("PixelFormat: ", cam.get_feature("PixelFormat"))
    #print("ExposureAuto: ", cam.get_feature("ExposureAuto"))
    print("PacketSize: ", cam.get_feature("GevSCPSPacketSize"))

    
    #cam.setup_stream()

    from IPython.frontend.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed()
    ipshell(local_ns=locals())

