from aravis import Camera

if __name__ == "__main__":
    #cam = ar.get_camera("Prosilica-02-2130A-06106")
    #cam = Camera("AT-Automation Technology GmbH-20805103")
    cam = Camera()
    ID = cam.get_device_id()
    path = cam.name + ".xml"
    print("Writing genicam to: ", path)
    f = open(path, "w")
    f.write(cam.get_genicam()[0])
    f.close()
 
