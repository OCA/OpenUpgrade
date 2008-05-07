#!/usr/bin/python
import sys
import xmpp
import os
import signal
import time

def presenceCB(conn,msg):
        print str(msg)
        prs_type=msg.getType()
        who=msg.getFrom()
        if prs_type == "subscribe":
                conn.send(xmpp.Presence(to=who, typ = 'subscribed'))
                conn.send(xmpp.Presence(to=who, typ = 'subscribe'))


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
        jid="dhp@tinyerp.com"
        pwd="dhp"

        jid=xmpp.protocol.JID(jid)

        cl = xmpp.Client(jid.getDomain(), debug=[])

        if cl.connect() == "":
                print "not connected"
                sys.exit(0)

        if cl.auth('dhp',pwd) == None:
                print "authentication failed"
                sys.exit(0)

        cl.RegisterHandler('presence', presenceCB)
        cl.sendInitPresence()

        GoOn(cl)

main()
