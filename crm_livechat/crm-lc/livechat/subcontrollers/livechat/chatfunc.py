# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
        close_chat = False
        print "msg lsit :::::::::::::\n", self.msglist,"\n"
        x = map(lambda x:x['message'], self.msglist)
        print "Mapping is this ................", x
        if 'closechat' in x:
            print "In Close chat >>>>>>>>>>>>"
            close_chat = True
        elif 'passchat' in x:
            print "No close chat .............."
        return dict(msglist = self.msglist,close_chat=close_chat)

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
        dis = {}
        if not (self.client):
            cl = self.myConnection(topicid)
            print "In main ................." , cl
            cl.RegisterHandler('presence', self.presenceCB)
            thread.start_new_thread(self.presencing,("Presencing",1,cl))
            c = cl.getRoster()
            dis = c._data
#            contactlist = []
#            for k,v in dis.items():
#                contactlist.append(str(k))
            cl.RegisterHandler('message', self.messageCB)
            cl.sendInitPresence()
            self.client=cl
            userlist = []
            for k,v in self.livechatdata['user'].items():
                userlist.append(str(self.livechatdata['user'][k]['login']))
            print "Users list are ****************", userlist
             
            self.users = rpc.RPCProxy('crm_livechat.livechat').get_user([int(topicid)])
            print "Users are available as ............", self.users

            for usr in self.users:
                self.user_id = usr
                print "Searching for user ::::::::::::::::", self.user_id           
                usrs = self.livechatdata['user'][str(usr)]['login']
                self.user= usrs
                print "The First user is this ....................", self.user
#                waitcounter = 0
#                while (not self.finalist.has_key(self.user)) and (dis.has_key(self.user)) and waitcounter < 5000:
#                    waitcounter = waitcounter + 1
#                    print "Waiting ....................>>>>>>>>>>>>>>>>>>"
#                if waitcounter == 5000:
#                    print "Waited Enough ..... assuming ", self.user , " is offline......."
                print "Final list is > > > > > > > >  > > > > >  > >  > > > >  > > > > > > >  >", self.finalist
                while not self.finalist.has_key(self.user):
                    pass
                if self.finalist[str(self.user)] == "online":   
                    self.sessionid = rpc.RPCProxy('crm_livechat.livechat').start_session([int(topicid)],False,self.partnerdata['id'])
                    print "Session is startedd :::::::::::::", self.sessionid
                    break
                else:
                    print "________________Priyesah"
                    clt="NoActive"
            print "After checking online ............................"
            if clt=='NoActive':
                return "Maximum Number of Connection exhausted."
            elif clt == 'ConError':
                return "Failed to Connect."
            else:
                self.cont = True
#                thread.start_new_thread(self.recieving,("Recieving",5,cl))
        else:
            print "MainHandler Called"
        print "Return Statement is ::::::::::::::::::"
        return "Active"

    def recieving(self,string,sleeptime,cl,*args):
        self.pcont = False
        recthread = ''
        while self.cont:
            recthread = os.getpid()
            try:
                v = cl.Process(1)
            except KeyboardInterrupt:
                return 0
                time.sleep(sleeptime)
        print "Flag receiving ended ................"
        self.cont = True
        return 0
    
    def presencing(self,string,sleeptime,cl,*args):
        prethread = ''
        while self.pcont:
            prethread = os.getpid()
            try:
                v = cl.Process(1)
            except KeyboardInterrupt, xml.parsers.expat.ExpatError:
                return 0
                time.sleep(sleeptime)
        print "Flag presencing ended ................"
#        self.pcont = True
        return 0

    @expose()
    def close_chat(self, **kw):
       print "In close chat functuion > > > > > > > > > > > > >"
       if(self.client):
           try:
               self.client.disconnect()
           except AttributeError:
               print "Attribute error :::::::::"
           print "Client is disconnected .............."
           self.client=None
       if (kw.get('close')):
           if self.logflag == True:
               self.logflag = False
               return {} 
           else:
               self.chat_log()
               print "Before session is stopped ::::::::::"
               res = rpc.RPCProxy('crm_livechat.livechat').stop_session(self.user_id,self.sessionid,True,self.logentry)   
               print "Final result is-------------->", res
               self.cont = False
               self.pcont = False
               self.msglist = []
       return {}
   
    def chat_log(self):
       print "Go into the Chat log Functtion ............."
       self.temp = []
       for i in range(len(self.newlist)):
         if  self.newlist[i] == 'UnknownCommand' or self.newlist[i] == 'Command':
             self.temp.append(self.newlist[i]) 
             print "Temporary is this . . . .  ............", self.temp
             continue
         else:
             self.temp.append(str(self.newlist[i]['sender'] + " : " + self.newlist[i]['message']))
             print "Temporary is as follows as ..............", self.temp
       b = '\n'.join(self.temp)
       print "B is .................", b
       cmnd = b.split('passchat')
       print "After Splitting the command is as follows .........................", cmnd
       self.logentry = '\n'.join(cmnd)
       print self.logentry,"-----------> "
   
#    def chat_log(self):
#       print "Go into the Chat log Functtion ............."
#       for i in range(len(self.msglist)):
#         if  self.msglist[i] == 'UnknownCommand' or self.msglist[i] == 'Command':
#             self.temp.append(self.msglist[i]) 
#             print "Temporary is this . . . .  ............", self.temp
#             continue
#         else:
#             self.temp.append(str(self.msglist[i]['sender'] + " : " + self.msglist[i]['message']))
#             print "Temporary is as follows as ..............", self.temp
#       b = '\n'.join(self.temp)
#       print "B is .................", b
#       cmnd = b.split('passchat')
#       print "After Splitting the command is as follows .........................", cmnd
#       self.logentry = '\n'.join(cmnd)
#       print self.logentry,"-----------> "
         
    @expose(format='json')
    def justsend(self,**kw):
        if not self.client == 'chatended':
            sendto = ''
            msg = kw.get('messg')
            if(self.user):
                print "sending",msg," :to:  ",self.user
                sendto = self.user
            self.recepients = sendto
            msg_obj = xmpp.protocol.Message(sendto,msg);
            try:
                self.client.send(msg_obj)
            except:
                print "Exception :::::::::"
                jid = self.logininfo['jid']
                jserver = self.logininfo['jserver']
                pwd = self.logininfo['pwd']
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
                
                self.client = cl
                self.client.send(msg_obj)
            msgformat = {"sender":str(self.login) , "message" : str(msg),"type":'sender'}
            self.msglist.append(msgformat)
            self.newlist.append(msgformat)
            return dict()
        return {}

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
            self.logininfo['jid'] = jid = self.partnerdata['jid']
            self.logininfo['jserver'] = jserver = self.partnerdata['server']
            self.logininfo['pwd']= pwd = self.partnerdata['pwd']
            self.login = jid
            
            jid=xmpp.protocol.JID(jid)
            cl=xmpp.Client(jid.getDomain(),debug=[])
            try:
                x = cl.connect((jserver,5223))
            except AttributeError:
                print "Exception Error ........."
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
        body = msg.getBody()
        print "Body Of masg is ::::::::::::", body
        who = str(msg.getFrom())
        who =  who.split('/')[0]
        print "Who is this ? .....Don .....Don ", who, self.user
        if str(who) == str(self.user):
            print "they are equals :::::::::::::"
            index=body.find('/')
            bdy=body[index:]
            print "BODY .............", bdy
            
            if bdy[0]=='/':
                command=bdy.split(' ')[0][1:]
                command = command.lower()
                print "Command ::::::::::::::", command
                if command=='pass':
                    body = 'passchat'
                    id = bdy.split(' ')[1]
                    if id == self.partid:
                        print "Given id is not Valid .................."
                    else :
                        self.newuser = id
                        self.newuser = self.newuser.split("'")[0]
                        print "New user is :::::::::::::::::::::", self.newuser
                        ids = self.sock.execute('crm2',3,'admin','crm_livechat.jabber','search',[('login','=',self.newuser)])
                        usr_id = ids[0]
                        self.uid = self.sock.execute('crm2',3,'admin','crm_livechat.livechat.user','search',[('jabber_id','=',usr_id)])
                        print "New users ids are here ::::::::::::::::::", self.uid[0]
                        if self.uid[0] in self.users:  
                            print "In message Cb function goes .............."
                            self.chat_log()
                            self.flagnewuser = True
                            self.Reghandler(id)
#                            cmd = 1
                        else:
                            print "User is not Avaliable at this topic ........... Plz try for another user ............ "
                
                elif command.split("'")[0] == 'close':
                    print "*****************************************************close"
                    body = 'closechat'
                    print "after body is > > > > > ..............", body
                    self.cont = False
                    self.pcont = False
                    self.client = 'chatended'
                    print "Receiving thread endeed ........ ok .........."
                    self.chat_log()
                    self.sock.execute('crm2',3,'admin','crm_livechat.livechat','stop_session',self.user_id,self.sessionid,True,self.logentry)
                    self.logflag = True
                    print "close chat is called :::::::::::::"
                    cmd = 0
                
                else:
                    cmd = -1
              
        print "Messsge arriving ..............", msg
        print "\nContent: " + str(msg.getBody())
        print "Sender: " + str(msg.getFrom())
        
        
        if not body == msg.getBody():
            msgformat = {"sender" : str(msg.getFrom()) , "message" : body , "timestamp" : str(msg.getTimestamp()),"type" : 'receiver'}
        else:
            msgformat = {"sender" : str(msg.getFrom()) , "message" : str(msg.getBody()) , "timestamp" : str(msg.getTimestamp()),"type" : 'receiver'}
        if cmd == 0:
            self.msglist.append(msgformat)
        elif cmd == -1:
            pass
        
        self.newlist.append(msgformat)
        
#            msgformat = {"sender" : 'Tiny Server' , "message" : "Unknown Command" , "timestamp" : str(msg.getTimestamp()),"type" : 'receiver'}
#            self.msglist.append('UnknownCommand')
#        elif cmd == 1:
#            self.msglist.append('Command')            
    
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
                rs = self.sock.execute('crm2',3,'admin','crm_livechat.livechat','stop_session',self.user_id,self.sessionid,True,self.logentry)
                self.newlist = []
                print "first Id ..............", self.user_id
                print "New id > > > > > > > > > > > > > > >", self.uid
                self.user_id = self.uid[0]
                print "New User id > > > > > > > > > > > > > > >", self.user_id
                if self.newuser: 
                    res = self.sock.execute('crm2',3,'admin','crm_livechat.livechat','start_session',[int(self.topicid)],True,self.partnerdata['id'])
                    self.user = self.newuser
                self.flagnewuser = False
                 
    newlist = []
    client = None
    recepients=[]
    msglist=[]
    user = ''
    sessionid = ''
    topicid = ''
    login = ''
    cont = True
    pcont = True
    finalist={}
    livechatdata={}
    partnerdata={}
    logentry = {}
    newuser = ''
    temp = []
    flagnewuser = False
    partid = ''
    user_id = ''
    users = []
    uid = []
    logininfo = {}
    logflag = False
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

