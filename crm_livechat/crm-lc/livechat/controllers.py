from turbogears import controllers, expose, flash,redirect
# from livechat import model
import sha, time
import sys,os,xmpp
import signal



class Root(controllers.RootController):
            
    @expose(template="livechat.templates.welcome")
    def index(self):
        pass
        raise redirect('/main_page')

    @expose(template="livechat.templates.main_page")
    def main_page(self):
        pass
        return dict()
    
 
    
       
    @expose(template="livechat.templates.chat_window")
    def chat_window(self,**kw):
        chat = {}
        chat['txtarea'] = ''
        print "kw::::",kw
#        chat['txtarea'] = kw.get('txtarea')
        print "Message received successfully",chat
        msg =  kw.get('txtarea')
        print "Message is ::::", msg
        jid="cza@tinyerp.com"
        pwd="cza"
        recipients=["pso@tinyerp.com"]
        jid=xmpp.protocol.JID(jid)
        cl=xmpp.Client(jid.getDomain(),debug=[])
        if cl.connect() == "":
            print "not connected"
            sys.exit(0)
        print "Connected....\n\nStarting to Authentication...."
        if cl.auth(jid.getNode(),pwd,"test") == None:
            print "authentication failed"
            sys.exit(0)
        print "Authenticated...."
        for recipient in recipients:
            print "send messages from" ,jid, "to" ,recipient
            cl.send(xmpp.protocol.Message(recipient,msg))
        print "Going to Disconnected........."
        #raise redirect('/main')
    #        self.main()
        return {}
        
#    @expose()
#    def callquit(self):
#        print "quit called"
#        self.quitflag = True
#        return {}        
#        
#    @expose()
#    def callmain(self):
#        print "main called"
#        self.main()
#        return {}
#       
        
    
    @expose()
    def messageCB(self, conn,msg):
        print "In messageCB::::::::"
        print "Message Receive.......";print "Sender: " + str(msg.getFrom())
        print "Content: " + str(msg.getBody())
        print "Message: ",msg
        
    @expose()
    def StepOn(self,conn):
        print "IN StepOn"
        
        try:
            print "CONNECTING"
            conn.Process(1)
        except KeyboardInterrupt:
            return 0
        else:
            return 1
            pass
        
        
    
    def GoOn(self,conn):
        print "in GoOn"
        while self.StepOn(conn):
            pass
            
#            if not self.quitflag:
#                print "passing...."
#                pass
#            else:
#                print "quitting"
#                return a
             

    
    
    @expose(template="livechat.templates.chat_window")
    def main(self):


        print "In main:::::::::"
        jid="cza@tinyerp.com"
        pwd="cza"
        jid=xmpp.protocol.JID(jid)
        cl = xmpp.Client(jid.getDomain(), debug=[])

        if cl.connect() == "":
                print "not connected"
                sys.exit(0)

        if cl.auth(jid.getNode(),pwd,"tempSend") == None:
                print "authentication failed"
                sys.exit(0)
                                
        cl.RegisterHandler('msg', self.messageCB)
        
        cl.sendInitPresence()
        print "Receiving...."
       
        
        self.GoOn(cl)
        return dict()
    
        
      
        
      
        
