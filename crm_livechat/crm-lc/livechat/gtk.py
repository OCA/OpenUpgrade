#!/usr/bin/python
import sys
import xmpp
import os
import signal
import time


        

def StepOn(conn):
        try:
               v = conn.Process(1)
               print "V::::::::::::::::", v
        except KeyboardInterrupt:
                return 0
        return 1

def GoOn(conn):
        while StepOn(conn):
                pass

def main():


        def messageCB(conn,msg):
            print "Messge Arriving", msg
            print "Sender: " + str(msg.getFrom())
            print "Content: " + str(msg.getBody())
            print "Message: ", msg

        jid="pso@tinyerp.com"
        pwd="pso"

        jid=xmpp.protocol.JID(jid)

        cl = xmpp.Client(jid.getDomain(), debug=[]);print "Conection Startring"

        if cl.connect() == "":
                print "not connected"
                sys.exit(0)
        print "Go in Else"

        if cl.auth(jid.getNode(),pwd,"tempSend") == None:
                print "authentication failed"
                sys.exit(0)
        print "System Exit"
        
        print "Register Hanslinfr"             
        cl.RegisterHandler('message', messageCB)
        print "Completer"
        
        cl.sendInitPresence();print "Receiving "

        GoOn(cl);print "Jumo odfg "

main()