from turbogears import controllers, expose, flash,redirect
# from livechat import model
import sha, time
import sys,os,xmpp
import signal


class Root(controllers.RootController):
    quitflag = False
    messagedict=['Hello', "Hi"]
    
    def __init__(self,username="pso@tinyerp.com",pwd="pso",res="psolocal"):
        print "Init sstart ,....."
        self.userid = "pso@tinyerp.com"
        self.password = "pso"
        self.resource = "psolocal"
        self.MessageBoard = ""
        self.jid=xmpp.protocol.JID(self.userid)
        self.Client = xmpp.Client(self.jid.getDomain(), debug=[])
        if self.Client.connect() == "":
                print "not connected"
                sys.exit(0)
        print "Connction finish.."
        if self.Client.auth(self.jid.getNode(),self.password,self.resource) == None:
                print "authentication failed"
                sys.exit(0)
        print "Auth Finished.."
        self.Client.RegisterHandler('msg', self.messageCB)
        print "Evend binding finishsed...."
        print "Init End..."
        self.Client.sendInitPresence()
        
                
    
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
        jid="pso@tinyerp.com"
        pwd="pso"
        recipients=["cza@tinyerp.com"]
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
        return dict()
        raise redirect('/main')
    

    @expose()
    def callmain(self):
        print "Main Called..."
        self.quitflag = False
        raise redirect('/main')

    
    @expose(template="livechat.templates.main_page")
    def callquit(self):
        print "Quit Called..."
        self.quitflag = True
        return {}
    
    @expose(template="livechat.templates.chatbox")
    def messageBox(self):
        print "calling....."
        i = 5000
        for i in range(10):
            print self.StepOn(self.Client)
        
        return dict(msgs=self.messagedict)
        
#        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
#        print "self: ",self
#        print "cl: ",self.Client
#        print "is connected : ",self.Client.isConnected()
#        if self.Client and self.Client.isConnected():
#            print "******************"
#            print "Client is already connected..."
#            self.messagedict.append("Hi this is Dhp")
#            return dict(msg=self.messagedict)
#        else:
#            print "#######################"
#            raise redirect('/authenticate')
#        
    

    def messageCB(self,conn,msg):
#        print "Message Receive.......";print "Sender: " + str(msg.getFrom())
#        print "Content: " + str(msg.getBody())
#        print "Message: ",msg
        print "message Recevier Called "
        if msg.getBody():
            self.messagedict.append(msg.getBody())
            print "Message Dict is updated to: ",self.messagedict
            
#        raise redirect('/messageBox')
     
   
    def StepOn(self,conn):
        print "inside stepon...."
        try:
            conn.Process(1)
        except KeyboardInterrupt:
            return 0
        return 1

    @expose()
    def GoOn(self,conn):
        print "calling Go on...."
        while StepOn(conn):
            pass

    @expose()
    def main(self):
#        print "Comming to Authe..."
#        jid="pso@tinyerp.com"
#        pwd="pso"
#        jid=xmpp.protocol.JID(jid);print "JID:::::::::",jid
#        cl = xmpp.Client(jid.getDomain(), debug=[])
#
#        if cl.connect() == "":
#                print "not connected"
#                sys.exit(0)
#
#        if cl.auth(jid.getNode(),pwd,"tempSend") == None:
#                print "authentication failed"
#                sys.exit(0)
#                                
#        cl.RegisterHandler('msg', messageCB)
#        
        print "Inside Authe...................."
        self.Client.sendInitPresence()
        print "Receiving...."

        GoOn(self.Client)
        
        
      

      
    
        
