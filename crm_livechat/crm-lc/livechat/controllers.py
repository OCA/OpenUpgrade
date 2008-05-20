from turbogears import controllers, expose, flash, redirect
import cherrypy
from cherrypy import request, response
import sha, time
import sys,os,xmpp
import signal
import thread
import xmlrpclib
import rpc
from rpc import *
import subcontrollers


class Root(controllers.RootController):
    client = None
    recepients=[]
    msglist=[]
    user = ''
    sessionid = ''
    topicid = ''

    chatfunc = subcontrollers.livechat.chatfunc.ChatFunc();
    
    @expose(template="livechat.templates.welcome")
    def index(self):
        print "Redirecting to ChatFunc"
        raise redirect('/chatfunc/index')
        
#    @expose(template="livechat.templates.chat_box")
#    def chatbox(self):
#        pass
#        expose(template="livechat.templates.chat_box")
#        return dict(msglist = self.msglist)
#
#    @expose(template="livechat.templates.main_page")
#    def main_page(self):
#        pass
#        return dict(topiclist = [])
#    
#    @expose(template="livechat.templates.main_page")
#    def select_topic(self,**kw):
#            proxy = rpc.RPCProxy("crm_livechat.livechat")
#            ids=proxy.search([])
#            res = proxy.read(ids, ['id','name','state','max_per_user'])
#            for i in range(0,len(res)):
#                rs = res[i]['name']
#                print rs,"----------------------"
#            return dict(topiclist = res)
#
#   
#    @expose(template="livechat.templates.chat_window")
#    def start_chat(self,topicid):
#        self.recepients = "Enter Sender ID Here"
#        cl=''
#        self.mainhandler(cl,topicid)
#        return dict(msglist = self.msglist,recepients = self.recepients)
#   
#    @expose()
#    def close_chat(self, **kw):
#       print "KW:::::::::",kw
#       if (kw.get('close')):
#           res = rpc.RPCProxy('crm_livechat.livechat').stop_session(int(self.topicid),int(self.sessionid))
#           print "Stops Session id::::::::::",res
#       return {}
# 
#   
#    def myConnection(self,topicid):
#        cr = ''
#        uid = ''
#        print "Gettin conf::: on :::::",topicid
#        self.topicid = topicid
#        livechatdata = rpc.RPCProxy('crm_livechat.livechat').get_configuration([int(topicid)])
#        print "Got conf:::",livechatdata
#        
#        partnerlist = livechatdata['partner']
#        pp=map(lambda p:p,partnerlist)
#        print "pp:::::",pp
#        
#        jid = livechatdata['partner'][pp[0]]['login']
#        pwd = livechatdata['partner'][pp[0]]['password']
#        print "Jabber ID--------", jid
#        print "Jabber Password-------", pwd
#             
#        jid=xmpp.protocol.JID(jid)
#        cl=xmpp.Client(jid.getDomain(),debug=[])
#        
#        if cl.connect() == "":
#                print "Connection Faild.... \nExiting"
#                sys.exit(0)
#        else:
#            print "Connected....\nStarting to Authenticate!!!!!!!!!!!!!!...."
#        
#        if cl.auth(jid.getNode(),pwd,"test") == None:
#                print "\nAuthentication Failed.... \nExiting..."
#                sys.exit(0)
#        else:
#            print "\nAuthenticated....\nClient Started....!!!!!!!!!!!!!!!!!\n\n"
#        
#        cl.RegisterHandler('message', self.messageCB)
#        cl.sendInitPresence();
#        
#        user = rpc.RPCProxy('crm_livechat.livechat').get_user([int(topicid)])
#        print "USER ::::::::::::",user
#        
#        user = livechatdata['user'][str(user)]['login']
#        print "User--------------------", user
#        self.user= user
#        
#        if(self.user):
#            self.sessionid = rpc.RPCProxy('crm_livechat.livechat').start_session([int(topicid)])
#        
#        return cl
#    
#    def messageCB(self,conn,msg):
#        print "Messge Arriving", msg
#        print "\nContent: " + str(msg.getBody())
#        print "Sender: " + str(msg.getFrom())
#        msgformat = str(msg.getFrom()) + " : "+str(msg.getBody())
#        self.msglist.append(msgformat)
#        
#    def recieving(self,string,sleeptime,cl,*args):
#        while 1:
#            try:
#                v = cl.Process(1)
#            except KeyboardInterrupt:
#                return 0
#                cl.disconnect()
#                print string," and sleep for ",sleeptime
#                time.sleep(sleeptime) 
#        
#    
#    def sending(self,string,sleeptime,cl,*args):
#        msgcounter = 0
#        while 1:
#            msgcounter = msgcounter + 1
#            print string," in ",sleeptime," secs "
#            cl.send(xmpp.protocol.Message("pso@tinyerp.com","\nMessage : "+str(msgcounter)+"\nHello How are you!!!!"))
#            time.sleep(sleeptime) 
#    
#    def mainhandler(self,cl,topicid):
#        print "Getting in MainHandler..."
#    
#        if not (cl):
#            print "Connection Not Found... \n Making Connetion again...\n"
#            cl = self.myConnection(topicid)
#            self.client = cl
#            print "",cl
#        else:
#            print "MainHandler Called"        
#    
#        print "\nStarting Thread to Recieve...."
#        thread.start_new_thread(self.recieving,("Recieving",5,cl))
#
#
#      
#        
##khudagawaah