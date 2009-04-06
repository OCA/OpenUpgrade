import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:5000')
s.import_data({'Test':'hello'})

