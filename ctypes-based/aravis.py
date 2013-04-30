import time
import numpy as np
from ctypes import POINTER, create_string_buffer, byref, Structure, cdll, Union
from ctypes import c_ulong, c_char, c_int, c_void_p, c_long, c_char_p, c_uint32, c_void_p, c_int64, c_float, c_bool, c_uint, c_double, c_int32, c_size_t, c_uint64, c_uint8
from ctypes import py_object, pythonapi



class AravisException(Exception):
    pass


class GError(Structure):
    _fields_ = [
        ('domain', c_uint32),
        ('code', c_int),
        ('message', c_char_p)
    ]


class GTypeClass(Structure):
    _fields_ = [
        ('g_type', c_ulong)
    ]

class GTypeInstance(Structure):
    _fields_ = [
        ('g_class', POINTER(GTypeClass)),
    ]

class GObject(Structure):
    _fields_ = [
        ('g_type_instance', GTypeInstance),
        ('ref_count', c_uint),
        ('qdata', c_void_p),
    ]

class GMutex(Union):
    _fields_ = [
        ('p', c_void_p),
        ('i', c_uint*2)
    ]

class GCond(Union):
    _fields_ = [
        ('p', c_void_p),
        ('i', c_uint*2)
    ]


class GList(Structure):
    pass

GList._fields_ = [
            ('data', POINTER(c_char)),
            ('next', POINTER(GList)),
            ('prev', POINTER(GList))
        ]


class GQueue(Structure):
    _fields_ = [
        ('head', POINTER(GList)),
        ('tail', POINTER(GList)),
        ('length', c_uint)
        ]

class GAsyncQueue(Structure):
    _fields_ = [
        ('mutex', POINTER(GMutex)),
        ('cond', POINTER(GCond)),
        ('queue', POINTER(GQueue)),
        ('waiting_threads', c_uint),
        ('ref_count', c_int32),
        ]

class ArvStreamPrivate(Structure):
    _fields_ = [
        ('input_queue', POINTER(GAsyncQueue)),
        ('output_queue', POINTER(GAsyncQueue)),
        ('emit_signal', c_bool)
    ]


class ArvStream(Structure):
    _fields_ = [
        ('object', GObject),
        ('object', ArvStreamPrivate)
            ]

class ArvDevice(Structure):
    _fields_ = [
        ('object', GObject),
        ('status', c_int),
        ('status_message', c_char_p)
            ]


class ArvBuffer(Structure):
    """
    /**
     * ArvBufferStatus:
          * @ARV_BUFFER_STATUS_SUCCESS: the buffer contains a valid image
           * @ARV_BUFFER_STATUS_CLEARED: the buffer is cleared
            * @ARV_BUFFER_STATUS_TIMEOUT: timeout was reached before all packets are received
             * @ARV_BUFFER_STATUS_MISSING_PACKETS: stream has missing packets
              * @ARV_BUFFER_STATUS_WRONG_PACKET_ID: stream has packet with wrong id
               * @ARV_BUFFER_STATUS_SIZE_MISMATCH: the received image didn't fit in the buffer data space
                * @ARV_BUFFER_STATUS_FILLING: the image is currently being filled
                 * @ARV_BUFFER_STATUS_ABORTED: the filling was aborted before completion
                  */
    """
    _fields_ = [
        ('object', GObject),
        ('size', c_size_t),
        ('is_preallocated', c_bool),
        ('data', POINTER(c_uint8)),
        ('user_data', c_void_p),
        ('user_data_destroy_func', c_void_p),
        ('status', c_uint),
        ('frame_id', c_uint32),
        ('timestamp_ns', c_uint64),
        ('x_offset', c_uint32),
        ('y_offset', c_uint32),
        ('width', c_uint32),
        ('height', c_uint32),
        ('pixel_format', c_uint32)
        ]
 
class ArvDomNode(Structure):
    pass

ArvDomNode._fields_ = [
        ('object', GObject),
        ('next_sibling', POINTER(ArvDomNode)),
        ('previous_sibling', POINTER(ArvDomNode)),
        ('parent_node', POINTER(ArvDomNode)),
        ('first_child', POINTER(ArvDomNode)),
        ('last_child', POINTER(ArvDomNode))
    ]
  

class ArDomDocument(Structure):
    _fields_ = [
        ('node', ArvDomNode),
	    ('url', c_char_p)
    ]


class ArvGc(Structure):
    _fields_ = [
        ('base', c_void_p), #ArvDomDocument
        ('node', c_void_p),
	    ('device', POINTER(ArvDevice))
    ]
 


class Aravis(object):
    def __init__(self, debug=""):
        self.dll = cdll.LoadLibrary("libaravis-0.4.so")
        if debug:
            self.dll.arv_debug_enable(debug)

        self.g = cdll.LoadLibrary("libgobject-2.0.so")
        self.g.g_type_init(None)
        self.gt = cdll.LoadLibrary("libgthread-2.0.so")
        self.gt.g_thread_init(None)
        self.dll.arv_debug_enable(None)

    def get_camera(self, serialid=None):
        handle = self.dll.arv_camera_new(serialid.encode())
        if handle:
            return Camera(self, handle)
        else:
            raise AravisException()

    def list_devices(self):
        self.dll.arv_update_device_list()
        nb_devices = self.dll.arv_get_n_devices()
        self.dll.arv_get_device_id.restype = c_char_p
        return [self.dll.arv_get_device_id(i) for i in range(0, nb_devices)]

    def get_cameras(self):
        return [self.get_camera(device) for device in self.list_devices()]



class Stream(object):
    def __init__(self, aravislib, stream):
        self.stream = stream
        self._ar = aravislib
        self._buf_from_memory = pythonapi.PyBuffer_FromMemory
        self._buf_from_memory.restype = py_object
        self.pixel_format = "Mono8"

    def set_timeout(self, val):
        self._ar.g.g_object_set(self.stream, "packet-timeout", val*1000)
 
    def push_new_buffer(self, size):
        self._ar.dll.arv_stream_push_buffer(self.stream, self.new_buffer(size))

    def push_buffer(self, buf):
        self._ar.dll.arv_stream_push_buffer(self.stream, buf)

    def new_buffer(self, size):
        self._ar.dll.arv_buffer_new.restype = POINTER(ArvBuffer)
        return self._ar.dll.arv_buffer_new(size, None)

    def pop_buffer(self):
        """
        pop buffer from queue. push it back when finished
        """
        self._ar.dll.arv_stream_pop_buffer.restype = POINTER(ArvBuffer)
        return self._ar.dll.arv_stream_pop_buffer(self.stream)

    def try_pop_buffer(self):
        """ non blocking version of pop """
        self._ar.dll.arv_stream_try_pop_buffer.restype = POINTER(ArvBuffer)
        buf = self._ar.dll.arv_stream_try_pop_buffer(self.stream)
        if buf: # this is necessary to avoid user try to access NULL pointer
            return buf
        else:
            return None

    def pop_array(self):
        buf = self.pop_buffer()
        return self._array_from_buffer(buf)

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
        im.shape = (buf.contents.height, buf.contents.width) 
        print("Shape: ", im.shape)
        im = im.copy()
        self.push_buffer(buf)
        return im

    def try_pop_array(self):
        buf = self.try_pop_buffer()
        return self._array_from_buffer(buf)


class Device(object):
    """
    access to a genicam device
    """
    def __init__(self, aravislib, dev):
        self._ar = aravislib
        self._dev = dev
        self._status_vals = {-1:"Uknown", 0:"Success", 1:"Timeout", 2:"Write_Error" }

    def get_status(self):
        self._ar.dll.arv_device_get_status.restype = c_int
        ret = self._ar.dll.arv_device_get_status(self._dev)
        return self._status_vals[ret]


    def execute_command(self, cmd):
        """
        run genicam command. command result can in theroy be seen with get_status....
        """
        self._ar.dll.arv_device_execute_command(self._dev, cmd)

    def get_genicam(self):
         self._ar.dll.arv_device_get_genicam.restype = ArvGc
         return self._ar.dll.arv_device_get_genicam(self._dev)

    def get_genicam_xml(self):
        self._ar.dll.arv_device_get_genicam_xml.restype = c_char_p
        size = c_size_t(1024)
        return self._ar.dll.arv_device_get_genicam_xml(self._dev, byref(size))

    def get_feature(self):
        #FIXME broken should return correct struct
        self._ar.dll.arv_device_get_feature.restype = c_char_p
        return self._ar.dll.arv_device_get_feature(self._dev)

    def get_string_feature(self, name):
        self._ar.dll.arv_device_get_string_feature_value.restype = c_char_p
        return self._ar.dll.arv_device_get_string_feature_value(self._dev, name)

    def set_string_feature(self, name, val):
        return self._ar.dll.arv_device_set_string_feature_value(self._dev, name, val)

    def get_integer_feature(self, name):
        self._ar.dll.arv_device_get_integer_feature_value.restype = c_int64
        return self._ar.dll.arv_device_get_integer_feature_value(self._dev, name)

    def set_integer_feature(self, name, val):
        val = c_int64(val)
        self._ar.dll.arv_device_set_integer_feature_value(self._dev, name, val)

    def get_float_feature(self, name):
        self._ar.dll.arv_device_get_float_feature_value.restype = c_double
        return self._ar.dll.arv_device_get_float_feature_value(self._dev, name)

    def set_float_feature(self, name, val):
        val = c_float(val)
        self._ar.dll.arv_device_set_float_feature_value(self._dev, name, val)

    def get_enum_vals(self, name) :
        """
        return possible values for enum feature
        """
        return self.get_available_enumeration_feature_values_as_strings(name)

    def get_available_enumeration_feature_values_as_strings(self, name):
        """
        const char **
        arv_device_get_available_enumeration_feature_values_as_strings (ArvDevice *device, const char *feature, guint *n_values)
        """
        nb = c_int()
        self._ar.dll.arv_device_get_available_enumeration_feature_values_as_strings.restype = POINTER(c_char_p) 
        res = self._ar.dll.arv_device_get_available_enumeration_feature_values_as_strings (self._dev, name, byref(nb))
        vals = []
        for i in range(0, nb.value):
            vals.append(res[i])
        return vals


    def read_memory(self, address, size):
        """
        read camera memory at given address
        """
        address = c_uint32(address)
        buf = create_string_buffer(size)
        size = c_uint32(size)
        res = self._ar.dll.arv_device_read_memory (self._dev, address, size, byref(buf), None)
        return buf.raw

    def write_memory(self, address, buf):
        """
        write Gige vision memory directly
        """
        address = c_uint32(address)
        size = c_uint32(len(buf))
        buf = create_string_buffer(buf)
        self._ar.dll.arv_device_write_memory.restype = c_bool
        res = self._ar.dll.arv_device_write_memory (self._dev, address, size, byref(buf), None)
        return res

    def read_register(self, address):
        """
        write Gige vision register directly
        """
        address = c_uint32(address)
        val = c_uint32()
        res = self._ar.dll.arv_device_read_register (self._dev, address, byref(val), None)
        return val.value

    def write_register(self, address, val):
        address = c_uint32(address)
        val = c_uint32(val)
        self._ar.dll.arv_device_write_register.restype = c_bool
        res = self._ar.dll.arv_device_write_register (self._dev, address, val, None)
        return res


class Camera(Device):
    """
    helper methods to communicate with a genicam camera
    """
    def __init__(self, aravislib, handle):
        self._ar = aravislib
        self._handle = handle
        Device.__init__(self, aravislib, self.get_device())

        self.name = self.get_vendor_name() + b"-" + self.get_device_id()
        self.stream  = self.create_stream()
        print("Created Camera object: ", self)
        

    def create_buffers(self, nb = 10):
        """
        add nb buffers to current stream
        do not change image size after calling this methos, otherwise buffers may be too small
        """
        payload = self.get_payload()
        for i in range(0, nb):
            self.stream.push_new_buffer(payload)

    def try_get_frame(self):
        """
        return last frame. Wait if no frame available
        """
        return self.stream.try_pop_array()

    def get_frame(self):
        """
        return last frame. Wait if no frame available
        Does not use directly C version since it may hang 
        """
        while True:
            frame = self.stream.try_pop_array()
            if frame != None:
                return frame
            else:
                time.sleep(0.005)

    def trigger(self):
        """
        trigger camera to take a picture in trigger source mode
        """
        self.execute_command("TriggerSoftware")

    def __str__(self):
        return "Camera: " + self.name

    def __repr__(self):
        return self.__str__()

    def get_device(self):
        self._ar.dll.arv_camera_get_device.restype = POINTER(ArvDevice)
        return self._ar.dll.arv_camera_get_device(self._handle)

    def get_sensor_size(self):
        width = c_int()
        height = c_int()
        self._ar.dll.arv_camera_get_sensor_size(self._handle, byref(width), byref(height))
        return width.value, height.value

    def get_region(self):
        x = c_int()
        y = c_int()
        width = c_int()
        height = c_int()
        self._ar.dll.arv_camera_get_region(self._handle, byref(x), byref(y), byref(width), byref(height))
        return x.value, y.value, width.value, height.value

    def set_region(self, x, y, width, height):
        self._ar.dll.arv_camera_set_region(self._handle, x, y, width, height)
   
    def get_exposure_time(self):
        self._ar.dll.arv_camera_get_exposure_time.restype = c_double
        return self._ar.dll.arv_camera_get_exposure_time (self._handle)

    def get_payload(self):
        self._ar.dll.arv_camera_get_payload.restype = c_uint
        return self._ar.dll.arv_camera_get_payload (self._handle)

    def get_frame_rate(self):
        self._ar.dll.arv_camera_get_frame_rate.restype = c_double
        return self._ar.dll.arv_camera_get_frame_rate (self._handle)

    def set_frame_rate(self, val):
        val = c_double(val)
        self._ar.dll.arv_camera_set_frame_rate (self._handle, val)

    def get_gain (self):
        self._ar.dll.arv_camera_get_gain.restype = c_double
        return self._ar.dll.arv_camera_get_gain (self._handle)

    def set_gain (self):
        self._ar.dll.arv_camera_set_gain.restype = c_double
        return self._ar.dll.arv_camera_set_gain (self._handle)

    def get_vendor_name (self):
        self._ar.dll.arv_camera_get_vendor_name.restype = c_char_p
        return self._ar.dll.arv_camera_get_vendor_name(self._handle)

    def get_model_name (self):
        self._ar.dll.arv_camera_get_model_name.restype = c_char_p
        return self._ar.dll.arv_camera_get_model_name(self._handle)

    def get_device_id (self):
        self._ar.dll.arv_camera_get_device_id.restype = c_char_p
        return self._ar.dll.arv_camera_get_device_id(self._handle)

    def set_acquisition_mode(self, mode):
        self._ar.dll.arv_camera_set_acquisition_mode (self._handle, mode)

    def set_trigger_source(self, mode):
        self._ar.dll.arv_camera_set_trigger_source (self._handle, mode)

    def get_trigger_source(self):
        self._ar.dll.arv_camera_get_trigger_source.restype = c_char_p 
        return self._ar.dll.arv_camera_get_trigger_source(self._handle)
    
    def start_acquisition(self):
        self.stream.pixel_format = self.get_string_feature("PixelFormat") 
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

    def create_stream(self):
        self._ar.dll.arv_camera_create_stream.restype = POINTER(ArvStream)
        return Stream(self._ar, self._ar.dll.arv_camera_create_stream(self._handle, None, None))

    def get_pixel_format_as_string(self): 
        self._ar.dll.arv_camera_get_pixel_format_as_string.restype = c_char_p 
        return self._ar.dll.arv_camera_get_pixel_format_as_string(self._handle)

    def cleanup(self):
        print(self.name, ": cleanup")
        self._ar.g.g_object_unref(self._handle)

    def __del__(self):
        self.cleanup()



if __name__ == "__main__":
    ar = Aravis()
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    cam = ar.get_camera("AT-Automation Technology GmbH-20805103")
    try:
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
        print("ExposureAuto: ", cam.get_string_feature("ExposureAuto"))
        print("PacketSize: ", cam.get_integer_feature("GevSCPSPacketSize"))

    
        cam.create_buffers()

        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        ipshell = InteractiveShellEmbed()
        ipshell(local_ns=locals())
    finally:
        cam.cleanup()
        
