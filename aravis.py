"""
High level pythonic interface to to the aravis library
"""

import time
import logging
import numpy as np
import ctypes
from gi.repository import Aravis

__author__ = "Olivier Roulet-Dubonnet, Morten Lind"
__copyright__ = "Copyright 2011-2013, Sintef Raufoss Manufacturing"
__license__ = "GPLv3"
__version__ = "0.5"

class AravisException(Exception):
    pass

class Camera(object):
    """
    Create a Camera object. 
    name is the camera ID in aravis.
    If name is None, the first found camera is used.
    If no camera is found an AravisException is raised.
    """
    def __init__(self, name=None, loglevel=logging.WARNING):
        self.logger = logging.getLogger(self.__class__.__name__)
        if len(logging.root.handlers) == 0: #dirty hack
            logging.basicConfig()
        self.logger.setLevel(loglevel)
        self.name = name
        try:
            self.cam = Aravis.Camera.new(name)
        except TypeError:
            if name:
                raise AravisException("Error the camera {} was not found".format(name))
            else:
                raise AravisException("Error no camera found")
        self.name = self.cam.get_model_name()
        self.logger.info("Camera object created for device: {}".format(self.name))
        self.dev = self.cam.get_device()
        self.stream = self.cam.create_stream(None, None)
        self._frame = None
        self._last_payload = 0

    def __getattr__(self, name):
        if hasattr(self.cam, name): # expose methods from the aravis camera object which is also relatively high level
            return getattr(self.cam, name)
        #elif hasattr(self.dev, name): #epose methods from the aravis device object, this might be confusing
        #    return getattr(self.dev, name)
        else:
            raise AttributeError(name)

    def __dir__(self):
        tmp = list(self.__dict__.keys()) + self.cam.__dir__()# + self.dev.__dir__()
        return tmp

    def load_config(self, path):
        """
        read a config file as written by stemmer imaging for example
        and apply the config to the camera
        """
        f = open(path)
        for line in f:
            if line.startswith("#"):
                continue
            else:
                name, val = line.split()
                name = name.strip()
                val = val.strip()
                self.logger.info("Config file: Setting {} to {} ".format( name, val))
                try:
                    self.set_feature(name, val)
                except AravisException as ex:
                    self.logger.warning(ex)
        f.close()

    def get_feature_type(self, name):
        genicam = self.dev.get_genicam()
        node = genicam.get_node(name)
        if not node:
            raise AravisException("Feature {} does not seem to exist in camera".format(name))
        return node.get_node_name()

    def get_feature(self, name):
        """
        return value of a feature. independantly of its type
        """
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
            self.logger.warning("Feature type not implemented: ", ntype)

    def set_feature(self, name, val):
        """
        set value of a feature
        """
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
            self.logger.warning("Feature type not implemented: ", ntype)

    def get_genicam(self):
        """
        return genicam xml from the camera
        """
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

    def create_buffers(self, nb=10, payload=None):
        if not payload:
            payload = self.cam.get_payload()
        self.logger.info("Creating {} memory buffers of size {}".format(nb, payload))
        for i in range(0, nb):
            self.stream.push_buffer(Aravis.Buffer.new_allocate(payload))

    def pop(self, timestamp=False):
        while True: #loop in python in order to allow interrupt, have the loop in C might hang
            if timestamp:
                ts, frame = self.try_pop(timestamp)
            else:
                frame = self.try_pop()

            if frame is None:
                time.sleep(0.001)
            else:
                if timestamp:
                    return ts, frame
                else:
                    return frame

    def try_pop(self, timestamp=False):
        """
        return the oldest frame in the aravis buffer
        """
        buf = self.stream.try_pop_buffer()
        if buf:
            frame = self._array_from_buffer_address(buf)
            self.stream.push_buffer(buf)
            if timestamp:
                return buf.timestamp_ns, frame
            else:
                return frame
        else:
            if timestamp:
                return None, None
            else:
                return None

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
        trigger camera to take a picture when camera is in software trigger mode
        """
        self.execute_command("TriggerSoftware")

    def __str__(self):
        return "Camera: " + self.name

    def __repr__(self):
        return self.__str__()
    
    def start_acquisition(self, nb_buffers=10):
        self.logger.info("starting acquisition")
        payload = self.cam.get_payload()
        if payload != self._last_payload:
            #FIXME should clear buffers
            self.create_buffers(nb_buffers, payload) 
            self._last_payload = payload
        self.cam.start_acquisition()

    def start_acquisition_trigger(self, nb_buffers=1):
        self.set_feature("AcquisitionMode", "Continuous") #no acquisition limits
        self.set_feature("TriggerSource", "Software") #wait for trigger t acquire image
        self.set_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition(nb_buffers)

    def start_acquisition_continuous(self, nb_buffers=20):
        self.set_feature("AcquisitionMode", "Continuous") #no acquisition limits
        #self.set_feature("TriggerSource", "Freerun") #as fast as possible
        #self.set_string_feature("TriggerSource", "FixedRate") 
        #self.set_feature("TriggerMode", "On") #Not documented but necesary
        self.start_acquisition(nb_buffers)

    def stop_acquisition(self):
        self.cam.stop_acquisition()

    def shutdown(self):
        self.logger.warning("It is not necessary to call shutdown in this version of python-aravis")





def get_device_ids():
    n = Aravis.get_n_devices()
    l = [Aravis.get_device_id(i) for i in range(0, n)]
    return l






if __name__ == "__main__":
    #cam = Camera("Prosilica-02-2110A-06145")
    #cam = Camera("AT-Automation Technology GmbH-20805103")
    cam = Camera(None)
    try:
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


        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell(local_ns=locals())
    finally:
        cam.shutdown()

