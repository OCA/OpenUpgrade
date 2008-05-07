#!/usr/bin/python
import sys,os,xmpp

def Sending(msg):
        msg=""
        jid="pso@tinyerp.com"
        pwd="pso"
        print "Start Process................"
        recipients=["cza@tinyerp.com"]
        print "Set the Jclient Params........."
        jid=xmpp.protocol.JID(jid)
        cl=xmpp.Client(jid.getDomain(),debug=[])
        print "\nStart Connecting..............."
        if cl.connect() == "":
            print "not connected"
            sys.exit(0)
        print "Connected....\n\nStarting to Authentication...."
        if cl.auth(jid.getNode(),pwd,"test") == None:
            print "authentication failed"
            sys.exit(0)
        print "Authenticated...."
        for recipient in recipients:
            print "send messages from pso to ",recipient
            cl.send(xmpp.protocol.Message(recipient,msg))
        print "Going to Disconnected........."
        cl.disconnect()
Sending("Priyesh Solanki Here")
