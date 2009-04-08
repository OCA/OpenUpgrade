import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:5000')
s.import_data([
    {'org':'X.Ltd','fn':'Mr.X','email':'x@xmail.com'},
    {'org':'Y.Ltd','fn':'Mr.Y','email':'y@ymail.com'},
    {'org':'X.Ltd','fn':'Mr.XX','email':'xx@xmail.com'},
    {'org':'X.Ltd','fn':'Mr.X2','email':'x2@xmail.com'},
    {'org':'Y.Ltd','fn':'Mr.Y1','email':'y1@ymail.com'},
    ])

