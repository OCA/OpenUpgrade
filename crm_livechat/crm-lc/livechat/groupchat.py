#!/usr/bin/python
import sys
import xmpp
import os
import signal
import time

def messageCB(conn,msg):
        if msg.getType() == "groupchat":
                print str(msg.getFrom()) +": "+  str(msg.getBody())
        if msg.getType() == "chat":
                print "private: " + str(msg.getFrom()) +  ":" +str(msg.getBody())

def presenceCB(conn,msg):
        print msg




def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt:
            return 0
    return 1

def GoOn(conn):
    while StepOn(conn):
            pass


def main():

        jid="user@domain.tld"
        pwd="secret"

        jid=xmpp.protocol.JID(jid)

        cl = xmpp.Client(jid.getDomain(), debug=[])

        cl.connect()

        cl.auth(jid.getNode(),pwd)


        cl.sendInitPresence()

        cl.RegisterHandler('message', messageCB)

        room = "castle_anthrax@conference.holy-gra.il/zoot"
        print "Joining " + room

        cl.send(xmpp.Presence(to=room))


        GoOn(cl)

main()