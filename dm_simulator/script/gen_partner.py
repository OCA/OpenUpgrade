import xmlrpclib

print "Host",
host = raw_input('=> ')

print "Port",
port = raw_input('=> ')

print "DataBase",
db = raw_input('=> ')


print "User",
user = raw_input('=> ')

print "Password",
pwd = raw_input('=> ')

print "Number of Partner",
no_partner = raw_input('=> ')

server = xmlrpclib.ServerProxy("http://"+host+':'+port+'/xmlrpc/object')


padding = len(no_partner)+1
for i in range(1,int(no_partner)+1):
    p_id = server.execute(db,int(user),pwd,'res.partner','create',{'name':str('P%%0%sd' % padding % i)})
    a_id = server.execute(db,int(user),pwd,'res.partner.address','create',{'name':str('Address of P%%0%sd' % padding % i),'partner_id':p_id})
    
    print p_id, a_id
    

