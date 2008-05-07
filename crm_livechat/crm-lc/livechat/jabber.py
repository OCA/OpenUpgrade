##   jabber.py
##
##   Copyright (C) 2001 Matthew Allum
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU Lesser General Public License as published
##   by the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU Lesser General Public License for more details.
##


"""\

__intro__

jabber.py is a Python module for the jabber instant messaging protocol.
jabber.py deals with the xml parsing and socket code, leaving the programmer
to concentrate on developing quality jabber based applications with Python.

The eventual aim is to produce a fully featured easy to use library for
creating both jabber clients and servers.

jabber.py requires at least python 2.0 and the XML expat parser module
( included in the standard Python distrubution ).

It is developed on Linux but should run happily on over Unix's and win32.

__Usage__

jabber.py basically subclasses the xmlstream classs and provides the
processing of jabber protocol elements into object instances as well
'helper' functions for parts of the protocol such as authentication
and roster management.

An example of usage for a simple client would be ( only psuedo code !)

<> Read documentation on jabber.org for the jabber protocol.

<> Birth a jabber.Client object with your jabber servers host

<> Define callback functions for the protocol elements you want to use
   and optionally a disconnection.

<> Authenticate with the server via auth method, or register via the
   reg methods to get an account.

<> Call requestRoster() and sendPresence()

<> loop over process(). Send Iqs,messages and presences by birthing
   them via there respective clients , manipulating them and using
   the Client's send() method.

<> Respond to incoming elements passed to your callback functions.

<> Find bugs :)


"""

# $Id: jabber.py,v 1.58 2004/01/18 05:27:10 snakeru Exp $

import xmlstream
import sha, time

debug=xmlstream.debug

VERSION = xmlstream.VERSION

False = 0;
True  = 1;

timeout = 300

DBG_INIT, DBG_ALWAYS = debug.DBG_INIT, debug.DBG_ALWAYS
DBG_DISPATCH = 'jb-dispatch'            ; debug.debug_flags.append( DBG_DISPATCH )
DBG_NODE = 'jb-node'                    ; debug.debug_flags.append( DBG_NODE)
DBG_NODE_IQ = 'jb-node-iq'              ; debug.debug_flags.append( DBG_NODE_IQ )
DBG_NODE_MESSAGE = 'jb-node-message'    ; debug.debug_flags.append( DBG_NODE_MESSAGE )
DBG_NODE_PRESENCE = 'jb-node-pressence' ; debug.debug_flags.append( DBG_NODE_PRESENCE )
DBG_NODE_UNKNOWN = 'jb-node-unknown'    ; debug.debug_flags.append( DBG_NODE_UNKNOWN )


#
# JANA core namespaces
#  from http://www.jabber.org/jana/namespaces.php as of 2003-01-12
#  "myname" means that namespace didnt have a name in the jabberd headers
#
NS_AGENT      = "jabber:iq:agent"
NS_AGENTS     = "jabber:iq:agents"
NS_AUTH       = "jabber:iq:auth"
NS_CLIENT     = "jabber:client"
NS_DELAY      = "jabber:x:delay"
NS_OOB        = "jabber:iq:oob"
NS_REGISTER   = "jabber:iq:register"
NS_ROSTER     = "jabber:iq:roster"
NS_XROSTER    = "jabber:x:roster" # myname
NS_SERVER     = "jabber:server"
NS_TIME       = "jabber:iq:time"
NS_VERSION    = "jabber:iq:version"

NS_COMP_ACCEPT  = "jabber:component:accept" # myname
NS_COMP_CONNECT = "jabber:component:connect" # myname



#
# JANA JEP namespaces, ordered by JEP
#  from http://www.jabber.org/jana/namespaces.php as of 2003-01-12
#  all names by jaclu
#
_NS_PROTOCOL  = "http://jabber.org/protocol" # base for other
NS_PASS       = "jabber:iq:pass" # JEP-0003
NS_XDATA      = "jabber:x:data" # JEP-0004
NS_RPC        = "jabber:iq:rpc" # JEP-0009
NS_BROWSE     = "jabber:iq:browse" # JEP-0011
NS_LAST       = "jabber:iq:last" #JEP-0012
NS_PRIVACY    = "jabber:iq:privacy" # JEP-0016
NS_XEVENT     = "jabber:x:event" # JEP-0022
NS_XEXPIRE    = "jabber:x:expire" # JEP-0023
NS_XENCRYPTED = "jabber:x:encrypted" # JEP-0027
NS_XSIGNED    = "jabber:x:signed" # JEP-0027
NS_P_MUC      = _NS_PROTOCOL + "/muc" # JEP-0045
NS_VCARD      = "vcard-temp" # JEP-0054


#
# Non JANA aproved, ordered by JEP
#  all names by jaclu
#
_NS_P_DISCO     = _NS_PROTOCOL + "/disco" # base for other
NS_P_DISC_INFO  = _NS_P_DISCO + "#info" # JEP-0030
NS_P_DISC_ITEMS = _NS_P_DISCO + "#items" # JEP-0030
NS_P_COMMANDS   = _NS_PROTOCOL + "/commands" # JEP-0050


"""
 2002-01-11 jaclu

 Defined in jabberd/lib/lib.h, but not JANA aproved and not used in jabber.py
 so commented out, should/could propably be removed...

 NS_ADMIN      = "jabber:iq:admin"
 NS_AUTH_OK    = "jabber:iq:auth:0k"
 NS_CONFERENCE = "jabber:iq:conference"
 NS_ENVELOPE   = "jabber:x:envelope"
 NS_FILTER     = "jabber:iq:filter"
 NS_GATEWAY    = "jabber:iq:gateway"
 NS_OFFLINE    = "jabber:x:offline"
 NS_PRIVATE    = "jabber:iq:private"
 NS_SEARCH     = "jabber:iq:search"
 NS_XDBGINSERT = "jabber:xdb:ginsert"
 NS_XDBNSLIST  = "jabber:xdb:nslist"
 NS_XHTML      = "http://www.w3.org/1999/xhtml"
 NS_XOOB       = "jabber:x:oob"
 NS_COMP_EXECUTE = "jabber:component:execute" # myname
"""


## Possible constants for Roster class .... hmmm ##
RS_SUB_BOTH    = 0
RS_SUB_FROM    = 1
RS_SUB_TO      = 2

RS_ASK_SUBSCRIBE   = 1
RS_ASK_UNSUBSCRIBE = 0

RS_EXT_ONLINE   = 2
RS_EXT_OFFLINE  = 1
RS_EXT_PENDING  = 0

#############################################################################

def ustr(what):
    """If sending object is already a unicode str, just
       return it, otherwise convert it using xmlstream.ENCODING"""
    if type(what) == type(u''):
        r = what
    else:
        try: r = what.__str__()
        except AttributeError: r = str(what)
        # make sure __str__() didnt return a unicode
        if type(r) <> type(u''):
            r = unicode(r,xmlstream.ENCODING,'replace')
    return r
xmlstream.ustr = ustr

class NodeProcessed(Exception): pass   # currently only for Connection._expectedIqHandler

class Connection(xmlstream.Client):
    """Forms the base for both Client and Component Classes"""
    def __init__(self, host, port, namespace,
                 debug=[], log=True, connection=xmlstream.TCP, hostIP=None, proxy=None):

        xmlstream.Client.__init__(self, host, port, namespace,
                                  debug=debug, log=log,
                                  connection=connection,
                                  hostIP=hostIP, proxy=proxy)
        self.handlers={}
        self.registerProtocol('unknown', Protocol)
        self.registerProtocol('iq', Iq)
        self.registerProtocol('message', Message)
        self.registerProtocol('presence', Presence)

        self.registerHandler('iq',self._expectedIqHandler,system=True)

        self._expected = {}

        self._id = 0;

        self.lastErr = ''
        self.lastErrCode = 0

    def setMessageHandler(self, func, type='', chainOutput=False):
        """Back compartibility method"""
        print "WARNING! setMessageHandler(...) method is obsolette, use registerHandler('message',...) instead."
        return self.registerHandler('message', func, type, chained=chainOutput)

    def setPresenceHandler(self, func, type='', chainOutput=False):
        """Back compartibility method"""
        print "WARNING! setPresenceHandler(...) method is obsolette, use registerHandler('presence',...) instead."
        return self.registerHandler('presence', func, type, chained=chainOutput)

    def setIqHandler(self, func, type='', ns=''):
        """Back compartibility method"""
        print "WARNING! setIqHandler(...) method is obsolette, use registerHandler('iq',...) instead."
        return self.registerHandler('iq', func, type, ns)

    def header(self):
        self.DEBUG("stream: sending initial header",DBG_INIT)
        str = u"<?xml version='1.0' encoding='UTF-8' ?>   \
                <stream:stream to='%s' xmlns='%s'" % ( self._host,
                                                       self._namespace )

        if self._outgoingID: str = str + " id='%s' " % self._outgoingID
        str = str + " xmlns:stream='http://etherx.jabber.org/streams'>"
        self.send(str)
        self.process(timeout)

    def send(self, what):
        """Sends a jabber protocol element (Node) to the server"""
        xmlstream.Client.write(self,ustr(what))

    def _expectedIqHandler(self, conn, iq_obj):
        if iq_obj.getAttr('id') and \
           self._expected.has_key(iq_obj.getAttr('id')):
            self._expected[iq_obj.getAttr('id')] = iq_obj
            raise NodeProcessed('No need for further Iq processing.')

    def dispatch(self,stanza):
        """Called internally when a 'protocol element' is received.
           Builds the relevant jabber.py object and dispatches it
           to a relevant function or callback."""
        name=stanza.getName()
        if not self.handlers.has_key(name):
            self.DEBUG("whats a tag -> " + name,DBG_NODE_UNKNOWN)
            name='unknown'
        else:
            self.DEBUG("Got %s stanza"%name, DBG_NODE)

        stanza=self.handlers[name][type](node=stanza)

        typ=stanza.getType()
        if not typ: typ=''
        try:
            ns=stanza.getQuery()
            if not ns: ns=''
        except: ns=''
        self.DEBUG("dispatch called for: name->%s ns->%s"%(name,ns),DBG_DISPATCH)

        typns=typ+ns
        if not self.handlers[name].has_key(ns): ns=''
        if not self.handlers[name].has_key(typ): typ=''
        if not self.handlers[name].has_key(typns): typns=''

        chain=[]
        for key in ['default',typ,ns,typns]: # we will use all handlers: from very common to very particular
            if key: chain += self.handlers[name][key]

        output=''
        user=True
        for handler in chain:
            try:
                if user or handler['system']:
                    if handler['chain']: output=handler['func'](self,stanza,output)
                    else: handler['func'](self,stanza)
            except NodeProcessed: user=False

    def registerProtocol(self,tag_name,Proto):
        """Registers a protocol in protocol processing chain. You MUST register
           a protocol before you register any handler function for it.
           First parameter, that passed to this function is the tag name that
           belongs to all protocol elements. F.e.: message, presence, iq, xdb, ...
           Second parameter is the [ancestor of] Protocol class, which instance will
           built from the received node with call

                if received_packet.getName()==tag_name:
                    stanza = Proto(node = received_packet)
        """
        self.handlers[tag_name]={type:Proto, 'default':[]}

    def registerHandler(self,name,handler,type='',ns='',chained=False, makefirst=False, system=False):
        """Sets the callback func for processing incoming stanzas.
           Multiple callback functions can be set which are called in
           succession. Callback can optionally raise an NodeProcessed error to
           stop stanza from further processing. A type and namespace attributes can
           also be optionally passed so the callback is only called when a stanza of
           this type is received. Namespace attribute MUST be omitted if you
           registering an Iq processing handler.

           If 'chainOutput' is set to False (the default), the given function
           should be defined as follows:

                def myCallback(c, p)

           Where the first parameter is the Client object, and the second
           parameter is the [ancestor of] Protocol object representing the stanza
           which was received.

           If 'chainOutput' is set to True, the output from the various
           handler functions will be chained together.  In this case,
           the given callback function should be defined like this:

                def myCallback(c, p, output)

           Where 'output' is the value returned by the previous
           callback function.  For the first callback routine, 'output' will be
           set to an empty string.

           'makefirst' argument gives you control over handler prioriy in its type
           and namespace scope. Note that handlers for particular type or namespace always
           have lower priority that common handlers.
        """
        if not type and not ns: type='default'
        if not self.handlers[name].has_key(type+ns): self.handlers[name][type+ns]=[]
        if makefirst: self.handlers[name][type+ns].insert({'chain':chained,'func':handler,'system':system})
        else: self.handlers[name][type+ns].append({'chain':chained,'func':handler,'system':system})

    def setDisconnectHandler(self, func):
        """Set the callback for a disconnect.
           The given function will be called with a single parameter (the
           connection object) when the connection is broken unexpectedly (eg,
           in response to sending badly formed XML).  self.lastErr and
           self.lastErrCode will be set to the error which caused the
           disconnection, if any.
        """
        self.disconnectHandler = func

    ## functions for sending element with ID's ##

    def waitForResponse(self, ID, timeout=timeout):
        """Blocks untils a protocol element with the given id is received.
           If an error is received, waitForResponse returns None and
           self.lastErr and self.lastErrCode is set to the received error.  If
           the operation times out (which only happens if a timeout value is
           given), waitForResponse will return None and self.lastErr will be
           set to "Timeout".
           Changed default from timeout=0 to timeout=300 to avoid hangs in
           scripts and such.
           If you _really_ want no timeout, just set it to 0"""
        ID = ustr(ID)
        self._expected[ID] = None
        has_timed_out = False

        abort_time = time.time() + timeout
        if timeout:
            self.DEBUG("waiting with timeout:%s for %s" % (timeout,ustr(ID)),DBG_NODE_IQ)
        else:
            self.DEBUG("waiting for %s" % ustr(ID),DBG_NODE_IQ)
        print "wait for response:",self._expected[ID],"-", ID,"-", has_timed_out
        while (not self._expected[ID]) and not has_timed_out:
            print "Entering Process"
            if not self.process(0.2):
                print "herer" 
                return None
            print "g"
            if timeout and (time.time() > abort_time):
                print "timed out"
                has_timed_out = True
                print "done::"               
            if has_timed_out:
                self.lastErr = "Timeout"
            return None
        response = self._expected[ID]
        del self._expected[ID]
        if response.getErrorCode():
            self.lastErr     = response.getError()
            self.lastErrCode = response.getErrorCode()
            return None
        return response

    def SendAndWaitForResponse(self, obj, ID=None, timeout=timeout):
        """Sends a protocol element object and blocks until a response with
           the same ID is received.  The received protocol object is returned
           as the function result. """
        if ID is None :
            ID = obj.getID()
            if ID is None:
                ID = self.getAnID()
                obj.setID(ID)
        ID = ustr(ID)
        self.send(obj)
        return self.waitForResponse(ID,timeout)

    def getAnID(self):
        """Returns a unique ID"""
        self._id = self._id + 1
        return ustr(self._id)

#############################################################################

class Client(Connection):
    """Class for managing a client connection to a jabber server."""
    def __init__(self, host, port=5222, debug=[], log=False,
                 connection=xmlstream.TCP, hostIP=None, proxy=None):

        Connection.__init__(self, host, port, NS_CLIENT, debug, log,
                            connection=connection, hostIP=hostIP, proxy=proxy)

        self.registerHandler('iq',self._IqRosterManage,'result',NS_ROSTER,system=True)
        self.registerHandler('iq',self._IqRosterManage,'set',NS_ROSTER,system=True)
        self.registerHandler('iq',self._IqRegisterResult,'result',NS_REGISTER,system=True)
        self.registerHandler('iq',self._IqAgentsResult,'result',NS_AGENTS,system=True)
        self.registerHandler('presence',self._presenceHandler,system=True)

        self._roster = Roster()
        self._agents = {}
        self._reg_info = {}
        self._reg_agent = ''

    def disconnect(self):
        """Safely disconnects from the connected server"""
        self.send(Presence(type='unavailable'))
        xmlstream.Client.disconnect(self)

    def sendPresence(self,type=None,priority=None,show=None,status=None):
        """Sends a presence protocol element to the server.
           Used to inform the server that you are online"""
        self.send(Presence(type=type,priority=priority,show=show,status=status))

    sendInitPresence=sendPresence

    def _presenceHandler(self, conn, pres_obj):
        who = ustr(pres_obj.getFrom())
        type = pres_obj.getType()
        self.DEBUG("presence type is %s" % type,DBG_NODE_PRESENCE)
        if type == 'available' or not type:
            self.DEBUG("roster setting %s to online" % who,DBG_NODE_PRESENCE)
            self._roster._setOnline(who,'online')
        elif type == 'unavailable':
            self.DEBUG("roster setting %s to offline" % who,DBG_NODE_PRESENCE)
            self._roster._setOnline(who,'offline')
        self._roster._setShow(who,pres_obj.getShow())
        self._roster._setStatus(who,pres_obj.getStatus())

    def _IqRosterManage(self, conn, iq_obj):
        "NS_ROSTER and type in [result,set]"
        for item in iq_obj.getQueryNode().getChildren():
            jid  = item.getAttr('jid')
            name = item.getAttr('name')
            sub  = item.getAttr('subscription')
            ask  = item.getAttr('ask')

            groups = []
            for group in item.getTags("group"):
                groups.append(group.getData())

            if jid:
                if sub == 'remove' or sub == 'none':
                    self._roster._remove(jid)
                else:
                    self._roster._set(jid=jid, name=name,
                                      groups=groups, sub=sub,
                                      ask=ask)
            else:
                self.DEBUG("roster - jid not defined ?",DBG_NODE_IQ)

    def _IqRegisterResult(self, conn, iq_obj):
        "NS_REGISTER and type==result"
        self._reg_info = {}
        for item in iq_obj.getQueryNode().getChildren():
            self._reg_info[item.getName()] = item.getData()

    def _IqAgentsResult(self, conn, iq_obj):
        "NS_AGENTS and type==result"
        self.DEBUG("got agents result",DBG_NODE_IQ)
        self._agents = {}
        for agent in iq_obj.getQueryNode().getChildren():
            if agent.getName() == 'agent': ## hmmm
                self._agents[agent.getAttr('jid')] = {}
                for info in agent.getChildren():
                    self._agents[agent.getAttr('jid')][info.getName()] = info.getData()

    def auth(self,username,passwd,resource):
        """Authenticates and logs in to the specified jabber server
           Automatically selects the 'best' authentication method
           provided by the server.
           Supports plain text, digest and zero-k authentication.

           Returns True if the login was successful, False otherwise.
        """
        print "In jabber -> auth"
        auth_get_iq = Iq(type='get')
        auth_get_iq.setID('auth-get')
        q = auth_get_iq.setQuery(NS_AUTH)
        q.insertTag('username').insertData(username)
        self.send(auth_get_iq)


        auth_response = self.waitForResponse("auth-get")
        if auth_response == None:
            return False # Error
        else:
            auth_ret_node = auth_response
        print "got herer:"
        auth_ret_query = auth_ret_node.getTag('query')
        self.DEBUG("auth-get node arrived!",(DBG_INIT,DBG_NODE_IQ))

        auth_set_iq = Iq(type='set')
        auth_set_iq.setID('auth-set')

        q = auth_set_iq.setQuery(NS_AUTH)
        q.insertTag('username').insertData(username)
        q.insertTag('resource').insertData(resource)

        if auth_ret_query.getTag('token'):

            token = auth_ret_query.getTag('token').getData()
            seq = auth_ret_query.getTag('sequence').getData()
            self.DEBUG("zero-k authentication supported",(DBG_INIT,DBG_NODE_IQ))
            hash = sha.new(sha.new(passwd).hexdigest()+token).hexdigest()
            for foo in xrange(int(seq)): hash = sha.new(hash).hexdigest()
            q.insertTag('hash').insertData(hash)

        elif auth_ret_query.getTag('digest'):

            self.DEBUG("digest authentication supported",(DBG_INIT,DBG_NODE_IQ))
            digest = q.insertTag('digest')
            digest.insertData(sha.new(
                self.getIncomingID() + passwd).hexdigest() )
        else:
            self.DEBUG("plain text authentication supported",(DBG_INIT,DBG_NODE_IQ))
            q.insertTag('password').insertData(passwd)

        iq_result = self.SendAndWaitForResponse(auth_set_iq)

        if iq_result==None:
             return False
        if iq_result.getError() is None:
            return True
        else:
           self.lastErr     = iq_result.getError()
           self.lastErrCode = iq_result.getErrorCode()
           # raise error(iq_result.getError()) ?
           return False
        return True

    ## Roster 'helper' func's - also see the Roster class ##

    def requestRoster(self):
        """Requests the roster from the server and returns a
           Roster() class instance."""
        rost_iq = Iq(type='get')
        rost_iq.setQuery(NS_ROSTER)
        self.SendAndWaitForResponse(rost_iq)
        self.DEBUG("got roster response",DBG_NODE_IQ)
        self.DEBUG("roster -> %s" % ustr(self._roster),DBG_NODE_IQ)
        return self._roster


    def getRoster(self):
        """Returns the current Roster() class instance. Does
           not contact the server."""
        return self._roster


    def addRosterItem(self, jid):
        """ Send off a request to subscribe to the given jid.
        """
        self.send(Presence(to=jid, type="subscribe"))


    def updateRosterItem(self, jid, name=None, groups=None):
        """ Update the information stored in the roster about a roster item.

            'jid' is the Jabber ID of the roster entry; 'name' is the value to
            set the entry's name to, and 'groups' is a list of groups to which
            this roster entry can belong.  If either 'name' or 'groups' is not
            specified, that value is not updated in the roster.
        """
        iq = Iq(type='set')
        item = iq.setQuery(NS_ROSTER).insertTag('item')
        item.putAttr('jid', ustr(jid))
        if name != None: item.putAttr('name', name)
        if groups != None:
            for group in groups:
                item.insertTag('group').insertData(group)
        dummy = self.SendAndWaitForResponse(iq) # Do we need to wait??


    def removeRosterItem(self,jid):
        """Removes an item with Jabber ID jid from both the
           server's roster and the local internal Roster()
           instance"""
        rost_iq = Iq(type='set')
        q = rost_iq.setQuery(NS_ROSTER).insertTag('item')
        q.putAttr('jid', ustr(jid))
        q.putAttr('subscription', 'remove')
        self.SendAndWaitForResponse(rost_iq)
        return self._roster

    ## Registration 'helper' funcs ##

    def requestRegInfo(self,agent=''):
        """Requests registration info from the server.
           Returns the Iq object received from the server."""
        if agent: agent = agent + '.'
        self._reg_info = {}
        reg_iq = Iq(type='get', to = agent + self._host)
        reg_iq.setQuery(NS_REGISTER)
        self.DEBUG("Requesting reg info from %s%s:" % (agent, self._host), DBG_NODE_IQ)
        self.DEBUG(ustr(reg_iq),DBG_NODE_IQ)
        return self.SendAndWaitForResponse(reg_iq)


    def getRegInfo(self):
        """Returns a dictionary of fields requested by the server for a
           registration attempt.  Each dictionary entry maps from the name of
           the field to the field's current value (either as returned by the
           server or set programmatically by calling self.setRegInfo(). """
        return self._reg_info


    def setRegInfo(self,key,val):
        """Sets a name/value attribute. Note: requestRegInfo must be
           called before setting."""
        self._reg_info[key] = val


    def sendRegInfo(self, agent=None):
        """Sends the populated registration dictionary back to the server"""
        if agent: agent = agent + '.'
        if agent is None: agent = ''
        reg_iq = Iq(to = agent + self._host, type='set')
        q = reg_iq.setQuery(NS_REGISTER)
        for info in self._reg_info.keys():
            q.insertTag(info).putData(self._reg_info[info])
        return self.SendAndWaitForResponse(reg_iq)


    def deregister(self, agent=None):
        """ Send off a request to deregister with the server or with the given
            agent.  Returns True if successful, else False.

            Note that you must be authorised before attempting to deregister.
        """
        if agent:
            agent = agent + '.'
            self.send(Presence(to=agent+self._host,type='unsubscribed'))       # This is enough f.e. for icqv7t or jit
        if agent is None: agent = ''
        q = self.requestRegInfo()
        kids = q.getQueryPayload()
        keyTag = kids.getTag("key")

        iq = Iq(to=agent+self._host, type="set")
        iq.setQuery(NS_REGISTER)
        iq.setQueryNode("")
        q = iq.getQueryNode()
        if keyTag != None:
            q.insertXML("<key>" + keyTag.getData() + "</key>")
        q.insertXML("<remove/>")

        result = self.SendAndWaitForResponse(iq)

        if result == None:
            return False
        elif result.getType() == "result":
            return True
        else:
            return False

    ## Agent helper funcs ##

    def requestAgents(self):
        """Requests a list of available agents.  Returns a dictionary
           containing information about each agent; each entry in the
           dictionary maps the agent's JID to a dictionary of attributes
           describing what that agent can do (as returned by the
           NS_AGENTS query)."""
        self._agents = {}
        agents_iq = Iq(type='get')
        agents_iq.setQuery(NS_AGENTS)
        self.SendAndWaitForResponse(agents_iq)
        self.DEBUG("agents -> %s" % ustr(self._agents),DBG_NODE_IQ)
        return self._agents

    def _discover(self,ns,jid,node=None):
        iq=Iq(to=jid,type='get',query=ns)
        if node: iq.putAttr('node',node)
        rep=self.SendAndWaitForResponse(iq)
        if rep: return rep.getQueryPayload()

    def discoverItems(self,jid,node=None):
        """ According to JEP-0030: jid is mandatory, name, node, action is optional. """
        ret=[]
        for i in self._discover(NS_P_DISC_ITEMS,jid,node):
            ret.append(i.attrs)
        return ret

    def discoverInfo(self,jid,node=None):
        """ According to JEP-0030:
            For identity: category, name is mandatory, type is optional.
            For feature: var is mandatory"""
        identities , features = [] , []
        for i in self._discover(NS_P_DISC_INFO,jid,node):
            if i.getName()=='identity': identities.append(i.attrs)
            elif i.getName()=='feature': features.append(i.getAttr('var'))
        return identities , features

#############################################################################

class Protocol(xmlstream.Node):
    """Base class for jabber 'protocol elements' - messages, presences and iqs.
       Implements methods that are common to all these"""
    def __init__(self, name=None, to=None, type=None, attrs=None, frm=None, payload=[], node=None):
        if not attrs: attrs={}
        if to: attrs['to']=to
        if frm: attrs['from']=frm
        if type: attrs['type']=type
        self._node=self
        xmlstream.Node.__init__(self, tag=name, attrs=attrs, payload=payload, node=node)

    def asNode(self):
        """Back compartibility method"""
        print 'WARNING! "asNode()" method is obsolette, use Protocol object as Node object instead.'
        return self

    def getError(self):
        """Returns the error string, if any"""
        try: return self.getTag('error').getData()
        except: return None


    def getErrorCode(self):
        """Returns the error code, if any"""
        try: return self.getTag('error').getAttr('code')
        except: return None


    def setError(self,val,code):
        """Sets an error string and code"""
        err = self.getTag('error')
        if not err:
            err = self.insertTag('error')
        err.putData(val)
        err.putAttr('code',str(code))


    def __repr__(self):
        return self.__str__()


    def getTo(self):
        """Returns the 'to' attribute as a JID object."""
        try: return JID(self.getAttr('to'))
        except: return None


    def getFrom(self):
        """Returns the 'from' attribute as a JID object."""
        try: return JID(self.getAttr('from'))
        except: return None


    def getType(self):
        """Returns the 'type' attribute of the protocol element."""
        try: return self.getAttr('type')
        except: return None


    def getID(self):
        """Returns the 'id' attribute of the protocol element."""
        try: return self.getAttr('id')
        except: return None


    def setTo(self,val):
        """Sets the 'to' element to the given JID."""
        self.putAttr('to', ustr(val))


    def setFrom(self,val):
        """Sets the 'from' element to the given JID."""
        self.putAttr('from', ustr(val))


    def setType(self,val):
        """Sets the 'type' attribute of the protocol element"""
        self.putAttr('type', val)


    def setID(self,val):
        """Sets the ID of the protocol element"""
        self.putAttr('id', val)


    def getX(self,index=0):
        """Returns the x namespace, optionally passed an index if there are
           multiple tags."""
        try: return self.getXNodes()[index].namespace
        except: return None


    def setX(self,namespace,index=0):
        """Sets the name space of the x tag. It also creates the node
           if it doesn't already exist."""
        x = self.getTag('x',index)
        if not x: x = self.insertTag('x')
        x.setNamespace(namespace)
        return x


    def setXPayload(self, payload, namespace=''):
        """Sets the Child of an 'x' tag. Can be a Node instance or an
           XML document"""
        x = self.setX(namespace)

        if type(payload) == type('') or type(payload) == type(u''):
                payload = xmlstream.NodeBuilder(payload).getDom()

        x.kids = [] # should be a method for this realy
        x.insertNode(payload)


    def getXPayload(self, val=None):
        """Returns the x tags' payload as a list of Node instances."""
        nodes = []
        if val is not None:
            if type(val) == type(""):
                for xnode in self.getTags('x'):
                    if xnode.getNamespace() == val: nodes.append(xnode.kids[0])
                return nodes
            else:
                try: return self.getTags('x')[val].kids[0]
                except: return None

        for xnode in self.getTags('x'):
            nodes.append(xnode.kids[0])
        return nodes


    def getXNode(self, val=None):
        """Returns the x Node instance. If there are multiple tags
           the first Node is returned. For multiple X nodes use getXNodes
           or pass an index integer value or namespace string to getXNode
           and if a match is found it will be returned."""
        if val is not None:
            nodes = []
            if type(val) == type(""):
                for xnode in self.getTags('x'):
                    if xnode.getNamespace() == val: nodes.append(xnode)
                return nodes
            else:
                try: return self.getTags('x')[val]
                except: return None
        else:
            try: return self.getTag('x')
            except: return None

    def getXNodes(self):
        """Returns a list of X nodes."""
        return self.getTags('x')

    def setXNode(self, val=''):
        """Sets the x tag's data to the given textual value."""
        self.insertTag('x').putData(val)

    def fromTo(self):
        """Swaps the element's from and to attributes.
           Note that this is only useful for writing components; if you are
           writing a Jabber client you shouldn't use this, because the Jabber
           server will set the 'from' field automatically."""
        tmp = self.getTo()
        self.setTo(self.getFrom())
        self.setFrom(tmp)

#############################################################################

class Message(Protocol):
    """Builds on the Protocol class to provide an interface for sending
       message protocol elements"""
    def __init__(self, to=None, body=None, type=None, subject=None, attrs=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'message', to=to, type=type, attrs=attrs, frm=frm, payload=payload, node=node)
        if body: self.setBody(body)
        if subject: self.setSubject(subject)
        # examine x tag and set timestamp if pressent
        try: self.setTimestamp( self.getTag('x').getAttr('stamp') )
        except: self.setTimestamp()

    def getBody(self):
        """Returns the message body."""
        try: return self.getTag('body').getData()
        except: return None


    def getSubject(self):
        """Returns the message's subject."""
        try: return self.getTag('subject').getData()
        except: return None


    def getThread(self):
        """Returns the message's thread ID."""
        try: return self.getTag('thread').getData()
        except: return None


    def getTimestamp(self):
        return self.time_stamp


    def setBody(self,val):
        """Sets the message body text."""
        body = self.getTag('body')
        if body:
            body.putData(val)
        else:
            body = self.insertTag('body').putData(val)


    def setSubject(self,val):
        """Sets the message subject text."""
        subj = self.getTag('subject')
        if subj:
            subj.putData(val)
        else:
            self.insertTag('subject').putData(val)


    def setThread(self,val):
        """Sets the message thread ID."""
        thread = self.getTag('thread')
        if thread:
            thread.putData(val)
        else:
            self.insertTag('thread').putData(val)


    def setTimestamp(self,val=None):
        if not val:
            val = time.strftime( '%Y%m%dT%H:%M:%S', time.gmtime( time.time()))
        self.time_stamp = val


    def buildReply(self, reply_txt=''):
        """Returns a new Message object as a reply to itself.
           The reply message has the 'to', 'type' and 'thread' attributes
           automatically set."""
        m = Message(to=self.getFrom(), body=reply_txt)
        if not self.getType() == None:
            m.setType(self.getType())
        t = self.getThread()
        if t: m.setThread(t)
        return m

    def build_reply(self, reply_txt=''):
        print "WARNING: build_reply method is obsolette. Use buildReply instead."
        return self.buildReply(reply_txt)

#############################################################################

class Presence(Protocol):
    """Class for creating and managing jabber <presence> protocol
       elements"""
    def __init__(self, to=None, type=None, priority=None, show=None, status=None, attrs=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'presence', to=to, type=type, attrs=attrs, frm=frm, payload=payload, node=node)
        if priority: self.setPriority(priority)
        if show: self.setShow(show)
        if status: self.setStatus(status)

    def getStatus(self):
        """Returns the presence status"""
        try: return self.getTag('status').getData()
        except: return None

    def getShow(self):
        """Returns the presence show"""
        try: return self.getTag('show').getData()
        except: return None

    def getPriority(self):
        """Returns the presence priority"""
        try: return self.getTag('priority').getData()
        except: return None

    def setShow(self,val):
        """Sets the presence show"""
        show = self.getTag('show')
        if show: show.putData(val)
        else: self.insertTag('show').putData(val)

    def setStatus(self,val):
        """Sets the presence status"""
        status = self.getTag('status')
        if status: status.putData(val)
        else: self.insertTag('status').putData(val)

    def setPriority(self,val):
        """Sets the presence priority"""
        pri = self.getTag('priority')
        if pri: pri.putData(val)
        else: self.insertTag('priority').putData(val)

#############################################################################

class Iq(Protocol):
    """Class for creating and managing jabber <iq> protocol
       elements"""
    def __init__(self, to=None, type=None, query=None, attrs=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'iq', to=to, type=type, attrs=attrs, frm=frm, payload=payload, node=node)
        if query: self.setQuery(query)

    def _getTag(self,tag):
        try: return self.getTag(tag).namespace
        except: return None

    def _setTag(self,tag,namespace):
        q = self.getTag(tag)
        if q:
            q.namespace = namespace
        else:
            q = self.insertTag(tag)
            q.setNamespace(namespace)
        return q


    def getList(self):
        "returns the list namespace"
        return self._getTag('list')

    def setList(self,namespace):
        return self._setTag('list',namespace)


    def getQuery(self):
        "returns the query namespace"
        return self._getTag('query')

    def setQuery(self,namespace):
        """Sets a query's namespace, and inserts a query tag if
           one doesn't already exist.  The resulting query tag
           is returned as the function result."""
        return self._setTag('query',namespace)


    def setQueryPayload(self, payload, add=False):
        """Sets a Iq's query payload.  'payload' can be either a Node
           structure or a valid xml document. The query tag is automatically
           inserted if it doesn't already exist."""
        q = self.getQueryNode()

        if q is None:
            q = self.insertTag('query')

        if type(payload) == type('') or type(payload) == type(u''):
                payload = xmlstream.NodeBuilder(payload).getDom()

        if not add: q.kids = []
        q.insertNode(payload)


    def getQueryPayload(self):
        """Returns the query's payload as a Node list"""
        q = self.getQueryNode()
        if q: return q.kids

    def getQueryNode(self):
        """Returns any textual data contained by the query tag"""
        try: return self.getTag('query')
        except: return None

    def setQueryNode(self, val):
        """Sets textual data contained by the query tag"""
        q = self.getTag('query')
        if q:
            q.putData(val)
        else:
            self.insertTag('query').putData(val)

#############################################################################

class Roster:
    """A Class for simplifying roster management. Also tracks roster
       item availability."""
    def __init__(self):
        self._data = {}
        self._listener = None
        ## unused for now ... ##
        self._lut = { 'both':RS_SUB_BOTH,
                      'from':RS_SUB_FROM,
                      'to':RS_SUB_TO }


    def setListener(self, listener):
        """ Set a listener function to be called whenever the roster changes.

            The given function will be called whenever the contents of the
            roster changes in response to a received <presence> or <iq> packet.
            The listener function should be defined as follows:

                def listener(action, jid, info)

            'action' is a string indicating what type of change has occurred:

                "add"     A new item has been added to the roster.
                "update"  An existing roster item has been updated.
                "remove"  A roster entry has been removed.

            'jid' is the Jabber ID (as a string) of the affected roster entry.

            'info' is a dictionary containing the information that has been
            added or updated for this roster entry.  This dictionary may
            contain any combination of the following:

                "name"    The associated name of this roster entry.
                "groups"  A list of groups associated with this roster entry.
                "online"  The roster entry's "online" value ("online",
                          "offline" or "pending").
                "sub"     The roster entry's subscription value ("none",
                          "from", "to" or "both").
                "ask"     The roster entry's ask value, if any (None,
                          "subscribe", "unsubscribe").
                "show"    The roster entry's show value, if any (None, "away",
                          "chat", "dnd", "normal", "xa").
                "status"  The roster entry's current 'status' value, if
                          specified.
        """
        self._listener = listener


    def getStatus(self, jid): ## extended
        """Returns the 'status' value for a Roster item with the given jid."""
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['status']
        return None


    def getShow(self, jid):   ## extended
        """Returns the 'show' value for a Roster item with the given jid."""
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['show']
        return None


    def getOnline(self,jid):  ## extended
        """Returns the 'online' status for a Roster item with the given jid.
           """
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['online']
        return None


    def getSub(self,jid):
        """Returns the 'subscription' status for a Roster item with the given
           jid."""
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['sub']
        return None


    def getName(self,jid):
        """Returns the 'name' for a Roster item with the given jid."""
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['name']
        return None


    def getGroups(self,jid):
        """ Returns the lsit of groups associated with the given roster item.
        """
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['groups']
        return None


    def getAsk(self,jid):
        """Returns the 'ask' status for a Roster item with the given jid."""
        jid = ustr(jid)
        if self._data.has_key(jid):
            return self._data[jid]['ask']
        return None


    def getSummary(self):
        """Returns a summary of the roster's contents.  The returned value is a
           dictionary mapping the basic (no resource) JIDs to their current
           availability status (online, offline, pending). """
        to_ret = {}
        for jid in self._data.keys():
            to_ret[jid] = self._data[jid]['online']
        return to_ret


    def getJIDs(self):
        """Returns a list of JIDs stored within the roster.  Each entry in the
           list is a JID object."""
        to_ret = [];
        for jid in self._data.keys():
            to_ret.append(JID(jid))
        return to_ret


    def getRaw(self):
        """Returns the internal data representation of the roster."""
        return self._data


    def isOnline(self,jid):
        """Returns True if the given jid is online, False if not."""
        jid = ustr(jid)
        if self.getOnline(jid) != 'online':
            return False
        else:
            return True


    def _set(self,jid,name,groups,sub,ask):
        # meant to be called by actual iq tag
        """Used internally - private"""
        jid = ustr(jid) # just in case
        online = 'offline'
        if ask: online = 'pending'
        if self._data.has_key(jid): # update it
            self._data[jid]['name'] = name
            self._data[jid]['groups'] = groups
            self._data[jid]['ask'] = ask
            self._data[jid]['sub'] = sub
            if self._listener != None:
                self._listener("update", jid, {'name' : name,
                                               'groups' : groups,
                                               'sub' : sub, 'ask' : ask})
        else:
            self._data[jid] = { 'name': name, 'groups' : groups, 'ask': ask,
                                'sub': sub, 'online': online, 'status': None,
                                'show': None}
            if self._listener != None:
                self._listener("add", jid, {'name' : name, 'groups' : groups,
                                            'sub' : sub, 'ask' : ask,
                                            'online' : online})


    def _setOnline(self,jid,val):
        """Used internally - private"""
        jid = ustr(jid)
        if self._data.has_key(jid):
            self._data[jid]['online'] = val
            if self._listener != None:
                self._listener("update", jid, {'online' : val})
        else:                      ## fall back
            jid_basic = JID(jid).getStripped()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['online'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'online' : val})


    def _setShow(self,jid,val):
        """Used internally - private"""
        jid = ustr(jid)
        if self._data.has_key(jid):
            self._data[jid]['show'] = val
            if self._listener != None:
                self._listener("update", jid, {'show' : val})
        else:                      ## fall back
            jid_basic = JID(jid).getStripped()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['show'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'show' : val})


    def _setStatus(self,jid,val):
        """Used internally - private"""
        jid = ustr(jid)
        if self._data.has_key(jid):
            self._data[jid]['status'] = val
            if self._listener != None:
                self._listener("update", jid, {'status' : val})
        else:                      ## fall back
            jid_basic = JID(jid).getStripped()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['status'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'status' : val})


    def _remove(self,jid):
        """Used internally - private"""
        if self._data.has_key(jid):
            del self._data[jid]
            if self._listener != None:
                self._listener("remove", jid, {})

#############################################################################

class JID:
    """A Simple class for managing jabber users id's """
    def __init__(self, jid='', node='', domain='', resource=''):
        if jid:
            if jid.find('@') == -1:
                self.node = ''
            else:
                bits = jid.split('@', 1)
                self.node = bits[0]
                jid = bits[1]

            if jid.find('/') == -1:
                self.domain = jid
                self.resource = ''
            else:
                self.domain, self.resource = jid.split('/', 1)
        else:
            self.node = node
            self.domain = domain
            self.resource = resource


    def __str__(self):
        jid_str = self.domain
        if self.node: jid_str = self.node + '@' + jid_str
        if self.resource: jid_str += '/' + self.resource
        return jid_str

    __repr__ = __str__


    def getNode(self):
        """Returns JID Node as string"""
        return self.node


    def getDomain(self):
        """Returns JID domain as string or None if absent"""
        return self.domain


    def getResource(self):
        """Returns JID resource as string or None if absent"""
        return self.resource


    def setNode(self,val):
        """Sets JID Node from string"""
        self.node = val


    def setDomain(self,val):
        """Sets JID domain from string"""
        self.domain = val


    def setResource(self,val):
        """Sets JID resource from string"""
        self.resource = val


    def getStripped(self):
        """Returns a JID string with no resource"""
        if self.node: return self.node + '@' + self.domain
        else: return self.domain

    def __eq__(self, other):
        """Returns whether this JID is identical to another one.
           The "other" can be a JID object or a string."""
        return str(self) == str(other)

#############################################################################

## component types

## Accept  NS_COMP_ACCEPT
## Connect NS_COMP_CONNECT
## Execute NS_COMP_EXECUTE

class Component(Connection):
    """docs to come soon... """
    def __init__(self, host, port, connection=xmlstream.TCP,
                 debug=[], log=False, ns=NS_COMP_ACCEPT, hostIP=None, proxy=None):
        Connection.__init__(self, host, port, namespace=ns, debug=debug,
                            log=log, connection=connection, hostIP=hostIP, proxy=proxy)
        self._auth_OK = False
        self.registerProtocol('xdb', XDB)


    def auth(self,secret):
        """will disconnect on failure"""
        self.send( u"<handshake id='1'>%s</handshake>"
                   % sha.new( self.getIncomingID() + secret ).hexdigest()
                  )
        while not self._auth_OK:
            self.DEBUG("waiting on handshake")
            self.process(1)

        return True


    def dispatch(self, root_node):
        """Catch the <handshake/> here"""
        if root_node.name == 'handshake': # check id too ?
            self._auth_OK = True
        Connection.dispatch(self, root_node)

#############################################################################

## component protocol elements

class XDB(Protocol):
    def __init__(self, attrs=None, type=None, frm=None, to=None, payload=[], node=None):
        Protocol.__init__(self, 'xdb', attrs=attrs, type=type, frm=frm, to=to, payload=payload, node=node)

#############################################################################

class Log(Protocol):
    ## eg: <log type='warn' from='component'>Hello Log File</log>
    def __init__(self, attrs=None, type=None, frm=None, to=None, payload=[], node=None):
        Protocol.__init__(self, 'log', attrs=attrs, type=type, frm=frm, to=to, payload=payload, node=node)

    def setBody(self,val):
        "Sets the log message text."
        self.getTag('log').putData(val)

    def getBody(self):
        "Returns the log message text."
        return self.getTag('log').getData()

#############################################################################

class Server:
    pass