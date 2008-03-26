#!/usr/bin/python2.5

from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import xmlrpclib
import time
import odms_server

# Define user/password
user = "admin"
password = "o2aevl8w"

# Tiny Prod db
username = 'oduser' #the user
pwd = 'o2aevl8w' #the password of the user
dbname = 'tiny' #the database
openerp_srv = '91.121.5.124'
vsnet = '10.1.0.'

sock_common = xmlrpclib.ServerProxy('http://'+openerp_srv+':8069/xmlrpc/common')

# Get the uid
uid = sock_common.login(dbname, username, pwd)
print "DEBUG : uid",uid
print "DEBUG : uid",type(uid)

#replace localhost with the address of the openerp server
sock = xmlrpclib.ServerProxy('http://'+openerp_srv+':8069/xmlrpc/object')
print "DEBUG : sock :",sock

# Start XML-RPC Server
server = SimpleXMLRPCServer(("192.168.129.70", 8000))
server.register_introspection_functions()
print "DEBUG : server :",server

def _check_access(u,p):
        if (u == user and p == password):
                return True
        return False

def create_vsv(u,p,subs,module_names):
        print "DEBUG - Accessing create_vsv"

        print "DEBUG - module_names :",module_names

        # Check access rights
        if not _check_access(u,p):
                print "DEBUG - Authentication Error"
                return 1
        print "DEBUG : ODMS Server - Creating new Virtual Server for subscription",subs

        # Install New Vserver
        vsid = odms_server.newvs()

        print "DEBUG - vsid", vsid

        if (vsid <> False):
                print "DEBUG : ODMS Server - vsid type :",type(vsid)
        else:
                print "DEBUG : ODMS Server - Error during Vserver creation"
                err = sock.execute(dbname, uid, pwd, 'odms.subscription', 'write', subs,
                        {'vserv_server_state':'error','vserver_id':False})
                return False

	vsip = vsnet+str(vsid)
        print "DEBUG - vsip", vsip

        res = sock.execute(dbname, uid, pwd, 'odms.vserver', 'create',
                 {'name':str(vsid),'ipaddress':vsip,'state':'active'})
        print "ODMS Server - DEBUG res vserver create :",res

        # Send installed state
        print "ODMS Server - DEBUG subs :",subs
        res1 = sock.execute(dbname, uid, pwd, 'odms.subscription', 'write', subs,{'vserv_server_state':'installed','vserver_id':res})
        print "ODMS Server - DEBUG res subs write :",res1
        print "ODMS Server - New vserver created"

        # Configure new vserver
        sock_vserv = xmlrpclib.ServerProxy('http://'+vsip+':8069/xmlrpc/object')
        print "ODMS Server - DEBUG sock_vserv :",sock_vserv

	time.sleep(10)
        # Install modules
        print "ODMS Server - DEBUG module_names :",module_names
        mod_ids = sock_vserv.execute('oddb', 3, 'admin', 'ir.module.module', 'search', [('name','in',module_names)])
        print "ODMS Server - DEBUG module ids :",mod_ids
        res = sock_vserv.execute('oddb', 3, 'admin', 'ir.module.module', 'write', mod_ids ,{'state':'uninstalled'})
        print "ODMS Server - DEBUG module res :",res
        base_id = sock_vserv.execute('oddb',3,'admin','ir.module.module','search',[('name','=','base')])
        print "ODMS Server - DEBUG base id :",base_id
        res = sock_vserv.execute('oddb', 3, 'admin', 'ir.module.module', 'write', base_id ,{'state':'installed'})
        print "ODMS Server - DEBUG base res :",res

        return True
server.register_function(create_vsv)

def create_web(u,p,subs,vsid,url):
        if not _check_access(u,p):
                print "DEBUG - Authentication Error"
                return 1

        # Install new web space
        wid = odms_server.newweb(vsid, url)

        print "DEBUG : ODMS Server - Creating new Web space for subscription",subs,"at",url
        res = sock.execute(dbname, uid, pwd, 'odms.subscription', 'write', subs, {'web_server_state':'installed'})
        print "ODMS Server - DEBUG res write :",res

        return True
server.register_function(create_web)

# Run the server's main loop
server.serve_forever()

