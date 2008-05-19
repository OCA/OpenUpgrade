from turbogears import controllers, expose, flash,redirect
import sys
import xmpp
import os
import signal
import time

class Root(controllers.RootController):
    
    @expose(template="livechat.templates.chat_window")
    def messageCB(conn,msg):
        print "Messge Arriving", msg
        print "Sender: " + str(msg.getFrom())
        print "Content: " + str(msg.getBody())
        

    def StepOn(self,conn):
        print "ghhhh"
        try:
            conn.Process(1)
        except KeyboardInterrupt:
                return 0
        return 1

    def GoOn(self,conn):
        while self.StepOn(conn):
                pass

    @expose(template="livechat.templates.chat_window")
    def main(self):

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
        cl.RegisterHandler('message', self.messageCB)
        print "Completer"
        
        cl.sendInitPresence();print "Receiving "

        self.GoOn(cl);print "Jumo odfg "

