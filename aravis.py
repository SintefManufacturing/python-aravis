import time
from threading import Thread, Lock, Condition
import numpy as np
import ctypes
from gi.repository import Aravis


class AravisException(Exception):
    pass

class Camera(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.cam = Aravis.Camera.new(name)
        self.dev = self.cam.get_device()
        self.stream = self.cam.create_stream(None, None)
        self._frame = None
        self._cond = Condition()
        self._lock = Lock()
        self._stopev = False
        self._acquisition_started = False
        self.start()

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
        """
        read a config file as written by stemmer imaging for example
        """
        f = open(path)
        for line in f:
            if line.startswith("#"):
                continue
            else:
                name, val = line.split()
                name = name.strip()
                val = val.strip()
                print("Config file: Setting {} to {} ".format( name, val))
                try:
                    self.set_feature(name, val)
                except AravisException as ex:
                    print(ex)
        f.close()

    def get_feature_type(self, name):
        genicam = self.dev.get_genicam()
        node = genicam.get_node(name)
        if not node:
            raise AravisException("Feature {} does not seem to exist in camera".format(name))
        return node.get_node_name()

    def get_feature(self, name):
        ntype = self.get_feature_type(name)
        if ntype in ("Enumeration", "String", "StringReg"):
            return self.dev.get_string_feature_value(name)
        elif ntype == "Integer":
            return self.dev.get_integer_feature_value(name)
        elif ntype == "Float":
            return self.dev.get_float_feature_value(name)
        elif ntype == "Boolean":
            return self.dev.get_integer_feature_value(name)
        else:
            print("Feature type not implemented: ", ntype)

    def set_feature(self, name, val):
        ntype = self.get_feature_type(name)
        if ntype in ( "String", "Enumeration", "StringReg"):
            return self.dev.set_string_feature_value(name, val)
        elif ntype == "Integer":
            return self.dev.set_integer_feature_value(name, int(val))
        elif ntype == "Float":
            return self.dev.set_float_feature_value(name, float(val))
        elif ntype == "Boolean":
            return self.dev.set_integer_feature_value(name, int(val))
        else:
            print("Feature type not implemented: ", ntype)

    def get_genicam(self):
        return self.dev.get_genicam_xml()

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

    def create_buffers(self, nb=10):
        payload = self.cam.get_payload()
        for i in range(0, nb):
            self.stream.push_buffer(Aravis.Buffer.new(payload))

    def run(self):
        while not self._stopev:
            if self._acquisition_started:
                buf = self.stream.try_pop_buffer()
                if buf:
                    tmp = self._array_from_buffer_address(buf)
                    self.stream.push_buffer(buf)
                    with self._lock:
                        self._frame = tmp
                    with self._cond:
                        self._cond.notifyAll()
            time.sleep(0.001)

    def shutdown(self):
        self._stopev = True

    def get_frame(self, wait=False):
        if wait:
            with self._cond:
                self._cond.wait()
        with self._lock:
            return self._frame

    def _array_from_buffer_address(self, buf):
        if not buf:
            return None
        if buf.pixel_format in (Aravis.PIXEL_FORMAT_MONO_8,
                Aravis.PIXEL_FORMAT_BAYER_BG_8):
            INTP = ctypes.POINTER(ctypes.c_uint8)
        else:
            INTP = ctypes.POINTER(ctypes.c_uint16)
        addr = buf.data
        ptr = ctypes.cast(addr, INTP)
        im = np.ctypeslib.as_array(ptr, (buf.height, buf.width))
        im = im.copy()
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
        empty, full = self.stream.get_n_buffers()
        if (empty + full) == 0:
            self.create_buffers(3) #FIXME: is there an optimal number of buffers?
        self._acquisition_started = True
        self.cam.start_acquisition()

    def start_acquisition_trigger(self):
        self.set_feature("AcquisitionMode", "Continuous") #no acquisition limits
        #self.set_feature("TriggerSource", "Software") #wait for trigger t acquire image
        #self.set_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition()

    def start_acquisition_continuous(self):
        self.set_feature("AcquisitionMode", "Continuous") #no acquisition limits
        #self.set_feature("TriggerSource", "Freerun") #as fast as possible
        #self.set_string_feature("TriggerSource", "FixedRate") 
        #self.set_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition()

    def stop_acquisition(self):
        self._acquisition_started = False
        self.cam.stop_acquisition()





def get_device_ids():
    n = Aravis.get_n_devices()
    l = [Aravis.get_device_id(i) for i in range(0, n)]
    return l






if __name__ == "__main__":
    #cam = Camera("Prosilica-02-2110A-06145")
    #cam = Camera("AT-Automation Technology GmbH-20805103")
    cam = Camera(None)
    #Aravis.enable_interface ("Fake")
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

