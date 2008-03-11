from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import base64

server = SimpleXMLRPCServer(("192.168.0.4",8000))
server.register_introspection_functions()

def get_contrib_list():
    return os.listdir("/home/tiny/contrib")

def get_publish_list():
    return os.listdir("/home/tiny/publish")

def publish_release(filecontent,filename):
    try:
        fp = file("/home/tiny/publish/"+filename,'wb')
        fp.write(base64.decodestring(filecontent))
    except Exception,e:
        print "============Exception==============",e
    return True
    
def get_release(filename):
    try:
        file_content = file("/home/tiny/publish/"+filename,'rb').read()
        return base64.encodestring(file_content)
    except Exception,e:
        print "============Exception==============",e
    return True   
    
def publish_contrib():
    try:
        fp = file("/home/tiny/contrib/"+filename,'wb')
        fp.write(base64.decodestring(filecontent))
    except Exception,e:
        print "============Exception==============",e
    return True    

def get_contrib(filename):
    try:
        file_content = file("/home/tiny/contrib/"+filename,'rb').read()
        return base64.encodestring(file_content)
    except Exception,e:
        print "============Exception==============",e
    return True   


        
        
server.register_function(get_contrib_list,'get_contrib_list')
server.register_function(get_publish_list)
server.register_function(publish_release)
server.register_function(get_release)
server.register_function(publish_contrib)
server.register_function(get_contrib)


server.serve_forever()