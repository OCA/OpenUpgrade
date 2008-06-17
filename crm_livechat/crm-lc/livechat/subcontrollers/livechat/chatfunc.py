from turbogears import controllers, expose, flash, redirect,config
import cherrypy
from cherrypy import request, response
import sha, time
import sys,os,xmpp
import signal
import thread
import xmlrpclib,socket
from livechat import rpc, common
from livechat.rpc import *
import jabber
import string

class ChatFunc(controllers.RootController):

    dbname = config.get('dbname', path="crm")
    dbuser = config.get('dbuser', path="crm")
    dbpwd = config.get('dbpwd', path="crm")
    
    sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

    @expose(template="livechat.templates.welcome")
    def index(self):
        print "\n","*"*50,"\nPlease CHECK the Settings in 'dev.cfg'...\n","*"*50,"\n"
        res = rpc.session.login(self.dbname, self.dbuser, self.dbpwd)
        raise redirect('/select_topic')

    @expose(format='json')
    def chatbox2(self):
        return dict(msglist = self.msglist)

    @expose(template="livechat.templates.main_page")
    def select_topic(self,**kw):
        proxy = rpc.RPCProxy("crm_livechat.livechat")
        ids = proxy.search([('name','not like','Dummy'+"%"),('state','=','active')])
        res = proxy.read(ids, ['id','name','state','max_per_user'])
        return dict(topiclist = res)

    @expose()
    def start_chat(self,**kw):
        cl=''
        topicid = kw.get('topicid')
        print "toppicid:::",topicid
        message = self.mainhandler(cl,topicid)
        return dict(message=message)

    @expose(template="livechat.templates.chat_window")
    def chat_window(self):
        return dict()

    def mainhandler(self,cl,topicid):
        clt = ""
        if not (self.client):
            cl = self.myConnection(topicid)
            
            cl.RegisterHandler('presence', self.presenceCB)
            thread.start_new_thread(self.presencing,("Presencing",2,cl))
            
            c = cl.getRoster()
            self.dis = c._data
            self.contactlist = []
            for k,v in self.dis.items():
                self.contactlist.append(str(k))
            cl.RegisterHandler('message', self.messageCB)
            cl.sendInitPresence()
            self.client=cl
            self.userlist = []
            for k,v in self.livechatdata['user'].items():
                self.userlist.append(str(self.livechatdata['user'][k]['login']))
            
            users = rpc.RPCProxy('crm_livechat.livechat').get_user([int(topicid)])
            for usr in users:
                print "Searching for user ::::::::::::::::", usr
                usr = self.livechatdata['user'][str(usr)]['login']
                self.user= usr
                print "The First user is this ....................", self.user
                while not self.finalist.has_key(self.user):
                    print "Waituing ....................>>>>>>>>>>>>>>>>>>"
                if self.finalist[str(self.user)] == "online":   
                    self.sessionid = rpc.RPCProxy('crm_livechat.livechat').start_session([int(topicid)],False,self.partnerdata['id'])
                else:
                    print "________________Priyesah"
                    clt="NoActive"
            
            if clt=='NoActive':
                return "Maximum Number of Connection exhausted."
            elif clt == 'ConError':
                return "Failed to Connect."
            else:
                self.cont = True
                thread.start_new_thread(self.recieving,("Recieving",5,cl))
        else:
            print "MainHandler Called"
        return "Active"

    def recieving(self,string,sleeptime,cl,*args):
        self.pcont = False
        while self.cont:
            self.recthread = os.getpid()
            try:
                v = cl.Process(1)
            except KeyboardInterrupt:
                return 0
                time.sleep(sleeptime)
        self.cont = True
        return 0
    
    def presencing(self,string,sleeptime,cl,*args):
        while self.pcont:
            self.prethread = os.getpid()
            try:
                v = cl.Process(1)
            except KeyboardInterrupt:
                return 0
                time.sleep(sleeptime)
        self.pcont = True
        return 0

    @expose()
    def close_chat(self, **kw):
       temp=[]
       if(self.client):
           self.client.disconnect()
           self.client=None
       if (kw.get('close')):
           for i in range(0,len(self.msglist)):
             if  self.msglist[i] == 'UnknownCommand' or self.msglist[i] == 'Command':
                 temp.append(self.msglist[i]) 
                 print "Temporary is this . . . .  ............", temp
                 continue
             else:
                 temp.append(str(self.msglist[i]['sender'] + " : " + self.msglist[i]['message']))
                 print "Temporary is as follows as ..............", temp
          
           b = '\n'.join(temp)
           cmd = b.split('Command')
           print "After Splitting the command is as follows .........................", cmd
           self.logentry = '\n'.join(cmd)
           print self.logentry,"-----------> First part "
           res = rpc.RPCProxy('crm_livechat.livechat').stop_session(self.topicid,self.sessionid,True,self.logentry)           
           print "Final result is-------------->", res
           self.msglist=[]
           self.cont = False
       return {}
   
    @expose(format='json')
    def justsend(self,**kw):
        sendto = ''
        msg = kw.get('messg')
        if(self.user):
            print "sending",msg," :to:  ",self.user
            sendto = self.user
        self.recepients = sendto
        msg_obj = xmpp.protocol.Message(sendto,msg);
        self.client.send(msg_obj)
        msgformat = {"sender":str(self.login) , "message" : str(msg),"type":'sender'}
        self.msglist.append(msgformat)
        return dict()

    def myConnection(self,topicid):
        cr = ''
        uid = ''
        self.topicid = topicid
        
        '''
        1. Partner Check
        2. User Availablity for support
        3. if 1 and 2 proceed else stop
        '''
        self.partnerdata=rpc.RPCProxy('crm_livechat.livechat.partner').get_live_parnter()
        self.partid = self.partnerdata['jid']
        print "Partner is this  :::::::::::::", self.partid 
        self.livechatdata = rpc.RPCProxy('crm_livechat.livechat').get_configuration(topicid)
       
        if self.livechatdata and self.partnerdata:
            jid = self.partnerdata['jid']
            jserver = self.partnerdata['server']
            self.login = jid
            pwd = self.partnerdata['pwd']
            jid=xmpp.protocol.JID(jid)
            cl=xmpp.Client(jid.getDomain(),debug=[])
            x = cl.connect((jserver,5223))

            if x == "":
                return "ConError"
            else:
                try:
                    auth = cl.auth(jid.getNode(),pwd,"test")
                except AttributeError, err:
                    raise common.error(_("Connection refused !"), _("%s \n Verify USERNAME and PASSWORD in Jabber Config" % err))
                
        return cl
   
    def messageCB(self,conn,msg):
        cmd = 0
        body = str(msg.getBody())
        who = str(msg.getFrom())
        who =  who.split('/')[0]
        print "Who is this ? .....Don .....Don ", who
        print "Self.user is this  ? ........", self.user 
        if str(who) == str(self.user):
            print "they are equals :::::::::::::"
            index=body.find('/')
            body=body[index:]
            
            if body[0]=='/':
                cmd = -1
                cmd=body.split(' ')[0][1:]
                
                if cmd.lower()=='pass':
                    id = body.split(' ')[1]
                    if id == self.partid:
                        print "Given id is not Valid .................."
                    else :
                        self.newuser = id
                        self.flagnewuser = True
                        self.Reghandler(id)
                        cmd = 1
    
                elif cmd.lower()=='close':
                    print "*****************************************************close"
          
        print "Messge Arriving", msg
        print "\nContent: " + str(msg.getBody())
        print "Sender: " + str(msg.getFrom())
        
        msgformat = {"sender" : str(msg.getFrom()) , "message" : str(msg.getBody()),"timestamp" : str(msg.getTimestamp()),"type" : 'receiver'}
        if cmd == 0:
            self.msglist.append(msgformat)
        elif cmd == -1:
            self.msglist.append('UnknownCommand')
        elif cmd == 1:
            self.msglist.append('Command')            
    
    def presenceCB(self,conn,prs):
        who=prs.getFrom()
        usr_type = prs.getType()
        show = prs.getShow()
        status = prs.getStatus()
        
        if len(str(who).split('/')[0]) == 1:
            check = who
        else:
            check = str(who).split('/')[0]
        
        if usr_type == 'unavailable':
            self.finalist[check] = 'offline'
        if usr_type == None and show == 'away' :    
            self.finalist[check] = 'away'
        elif usr_type == None and show == None:
            self.finalist[check] = 'online'
                      
    def Reghandler(self, user):
        if self.flagnewuser:
            if self.finalist[self.newuser] == "online":
                rs = self.sock.execute('crm2',3,'admin','crm_livechat.livechat','stop_session',self.topicid,self.sessionid,True,self.logentry)
                if self.newuser:         
                    res = self.sock.execute('crm2',3,'admin','crm_livechat.livechat','start_session',[int(self.topicid)],True,self.partnerdata['id'])
                    self.user = self.newuser
                self.flagnewuser = False
                 
    client = None
    recepients=[]
    msglist=[]
    user = ''
    sessionid = ''
    topicid = ''
    mainthread = ''
    prethread = ''
    recthread = ''
    login = ''
    cont = True
    pcont = True
    dis = {}
    finalist={}
    userlist = []
    contactlist=[]
    livechatdata={}
    partnerdata={}
    logentry = {}
    newuser = ''
    flagnewuser = False
    partid = ''
  
  