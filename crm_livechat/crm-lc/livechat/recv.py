#!/usr/bin/python
import sys
import xmpp
import os
import signal
import time


def messageCB(conn,msg):
        print "Message Receive.......";print "Sender: " + str(msg.getFrom())
        print "Content: " + str(msg.getBody())
        print "Message: ",msg


def StepOn(conn):
		print "INN TRY :::::::::"
		try:
			conn.Process(1)
		except KeyboardInterrupt:
			return 0
		return 1

def GoOn(conn):
		print "IN GO ON ::::::::"
		while StepOn(conn):
			pass

def main():

        jid="pso@tinyerp.com"
        pwd="pso"
        jid=xmpp.protocol.JID(jid);print "JID:::::::::",jid
        cl = xmpp.Client(jid.getDomain(), debug=[])

        if cl.connect() == "":
                print "not connected"
                sys.exit(0)

        if cl.auth(jid.getNode(),pwd,"tempSend") == None:
                print "authentication failed"
                sys.exit(0)
                                
		cl.RegisterHandler('msg', messageCB)
		
        cl.sendInitPresence()
        print "Receiving...."

        GoOn(cl)

main()
