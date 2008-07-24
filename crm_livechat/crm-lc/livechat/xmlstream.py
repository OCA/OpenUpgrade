# -*- encoding: utf-8 -*-
##   xmlstream.py
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


"""\
xmlstream.py provides simple functionality for implementing
XML stream based network protocols. It is used as a  base
for jabber.py.

xmlstream.py manages the network connectivity and xml parsing
of the stream. When a complete 'protocol element' ( meaning a
complete child of the xmlstreams root ) is parsed the dipatch
method is called with a 'Node' instance of this structure.
The Node class is a very simple XML DOM like class for
manipulating XML documents or 'protocol elements' in this
case.

"""

# $Id: xmlstream.py,v 1.45 2004/02/03 16:33:37 snakeru Exp $

import time, sys, re, socket
from select import select
from base64 import encodestring
import xml.parsers.expat
import debug
_debug=debug

VERSION = "0.5"

False = 0
True  = 1

TCP     = 1
STDIO   = 0
TCP_SSL = 2

ENCODING = 'utf-8'      # Though it is uncommon, this is the only right setting.
ustr = str

BLOCK_SIZE  = 1048576

DBG_INIT, DBG_ALWAYS = debug.DBG_INIT, debug.DBG_ALWAYS
DBG_CONN_ERROR = 'conn-error'    ; debug.debug_flags.append( DBG_CONN_ERROR )
DBG_XML_PARSE = 'xml-parse'      ; debug.debug_flags.append( DBG_XML_PARSE )
DBG_XML_RAW = 'xml-raw'          ; debug.debug_flags.append( DBG_XML_RAW )
DBG_XML = [ DBG_XML_PARSE, DBG_XML_RAW ] # sample multiflag


def XMLescape(txt):
    "Escape XML entities"
    txt = txt.replace("&", "&amp;")
    txt = txt.replace("<", "&lt;")
    txt = txt.replace(">", "&gt;")
    return txt

def XMLunescape(txt):
    "Unescape XML entities"
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&amp;", "&")
    return txt

class error:
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return self.value

class Node:
    """A simple XML DOM like class"""
    def __init__(self, tag=None, parent=None, attrs={}, payload=[], node=None):
        if node:
            if type(node)<>type(self): node=NodeBuilder(node).getDom()
            self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = \
                node.name,node.namespace,node.attrs,node.data,node.kids,node.parent
        else:
            self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = 'tag','',{},[],[],None

        if tag: self.namespace, self.name = (['']+tag.split())[-2:]

        if parent: self.parent = parent

#        if self.parent and not self.namespace: self.namespace=self.parent.namespace   # Doesn't checked if this neccessary

        for attr in attrs.keys():
            self.attrs[attr]=attrs[attr]

        for i in payload:
            if type(i)==type(self): self.insertNode(i)
            else: self.insertXML(i)
#            self.insertNode(Node(node=i))     # Alternative way. Needs perfomance testing.

    def setParent(self, node):
        "Set the nodes parent node."
        self.parent = node

    def getParent(self):
        "return the nodes parent node."
        return self.parent

    def getName(self):
        "Set the nodes tag name."
        return self.name

    def setName(self,val):
        "Set the nodes tag name."
        self.name = val

    def putAttr(self, key, val):
        "Add a name/value attribute to the node."
        self.attrs[key] = val

    def getAttr(self, key):
        "Get a value for the nodes named attribute."
        try: return self.attrs[key]
        except: return None

    def putData(self, data):
        "Set the nodes textual data"
        self.data.append(data)

    def insertData(self, data):
        "Set the nodes textual data"
        self.data.append(data)

    def getData(self):
        "Return the nodes textual data"
        return ''.join(self.data)

    def getDataAsParts(self):
        "Return the node data as an array"
        return self.data

    def getNamespace(self):
        "Returns the nodes namespace."
        return self.namespace

    def setNamespace(self, namespace):
        "Set the nodes namespace."
        self.namespace = namespace

    def insertTag(self, name=None, attrs={}, payload=[], node=None):
        """ Add a child tag of name 'name' to the node.

            Returns the newly created node.
        """
        newnode = Node(tag=name, parent=self, attrs=attrs, payload=payload, node=node)
        self.kids.append(newnode)
        return newnode

    def insertNode(self, node):
        "Add a child node to the node"
        self.kids.append(node)
        return node

    def insertXML(self, xml_str):
        "Add raw xml as a child of the node"
        newnode = NodeBuilder(xml_str).getDom()
        self.kids.append(newnode)
        return newnode

    def __str__(self):
        return self._xmlnode2str()

    def _xmlnode2str(self, parent=None):
        """Returns an xml ( string ) representation of the node
         and it children"""
        s = "<" + self.name
        if self.namespace:
            if parent and parent.namespace != self.namespace:
                s = s + " xmlns = '%s' " % self.namespace
        for key in self.attrs.keys():
            val = ustr(self.attrs[key])
            s = s + " %s='%s'" % ( key, XMLescape(val) )
        s = s + ">"
        cnt = 0
        if self.kids != None:
            for a in self.kids:
                if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
                s = s + a._xmlnode2str(parent=self)
                cnt=cnt+1
        if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
        if not self.kids and s[-1:]=='>':
            s=s[:-1]+' />'
        else:
            s = s + "</" + self.name + ">"
        return s

    def getTag(self, name, index=None):
        """Returns a child node with tag name. Returns None
        if not found."""
        for node in self.kids:
            if node.getName() == name:
                if not index: return node
                if index is not None: index-=1
        return None

    def getTags(self, name):
        """Like getTag but returns a list with matching child nodes"""
        nodes=[]
        for node in self.kids:
            if node.getName() == name:
               nodes.append(node)
        return nodes

    def getChildren(self):
        """Returns a nodes children"""
        return self.kids

    def removeTag(self,tag):
        """Pops out specified child and returns it."""
        if type(tag)==type(self):
            try:
                self.kids.remove(tag)
                return tag
            except: return None
        for node in self.kids:
            if node.getName()==tag:
                self.kids.remove(node)
                return node

class NodeBuilder:
    """builds a 'minidom' from data parsed to it. Primarily for insertXML
       method of Node"""
    def __init__(self,data=None):
        self._parser = xml.parsers.expat.ParserCreate(namespace_separator=' ')
        self._parser.StartElementHandler  = self.unknown_starttag
        self._parser.EndElementHandler    = self.unknown_endtag
        self._parser.CharacterDataHandler = self.handle_data

        self.__depth = 0
        self._dispatch_depth = 1

        if data: self._parser.Parse(data,1)

    def unknown_starttag(self, tag, attrs):
        """XML Parser callback"""
        self.__depth = self.__depth + 1
        self.DEBUG("DEPTH -> %i , tag -> %s, attrs -> %s" % \
                   (self.__depth, tag, str(attrs)),DBG_XML_PARSE )
        if self.__depth == self._dispatch_depth:
            self._mini_dom = Node(tag=tag, attrs=attrs)
            self._ptr = self._mini_dom
        elif self.__depth > self._dispatch_depth:
            self._ptr.kids.append(Node(tag=tag,parent=self._ptr,attrs=attrs))
            self._ptr = self._ptr.kids[-1]
        else:                           ## it the stream tag:
            if attrs.has_key('id'):
                self._incomingID = attrs['id']
        self.last_is_data = False

    def unknown_endtag(self, tag ):
        """XML Parser callback"""
        self.DEBUG("DEPTH -> %i" % self.__depth,DBG_XML_PARSE)
        if self.__depth == self._dispatch_depth:
            self.dispatch(self._mini_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent
        else:
            self.DEBUG("*** Stream terminated ? ****",DBG_CONN_ERROR)
        self.__depth = self.__depth - 1
        self.last_is_data = False

    def handle_data(self, data):
        """XML Parser callback"""
        self.DEBUG("data-> " + data,DBG_XML_PARSE)
        if self.last_is_data:
            self._ptr.data[-1] += data
        else:
            self._ptr.data.append(data)
            self.last_is_data = True

    def dispatch(self,dom):
        pass

    def DEBUG(self,dup1,dup2=None):
        pass

    def getDom(self):
        return self._mini_dom


class Stream(NodeBuilder):
    """Extention of NodeBuilder class. Handles stream of XML stanzas.
       Calls dispatch method for every child of root node
       (stream:stream for jabber stream).
       attributes _read, _write and _reader must be set by external entity
    """
    def __init__(self, namespace,
                 debug=[DBG_ALWAYS],
                 log=None,
                 id=None,
                 timestampLog=True):

        self._namespace = namespace

        self._read , self._reader , self._write = None , None , None

        self._incomingID = None
        self._outgoingID = id

        self._debug = _debug.Debug(debug,encoding=ENCODING)
        self.DEBUG = self._debug.show # makes it backwards compatible with v0.4 code

        self.DEBUG("stream init called",DBG_INIT)

        if log:
            if type(log) is type(""):
                try:
                    self._logFH = open(log,'w')
                except:
                    print "ERROR: can open %s for writing" % log
                    sys.exit(0)
            else: ## assume its a stream type object
                self._logFH = log
        else:
            self._logFH = None
        self._timestampLog = timestampLog

    def connect(self):
        NodeBuilder.__init__(self)
        self._dispatch_depth = 2

    def timestampLog(self,timestamp):
        """ Enable or disable the showing of a timestamp in the log.
            By default, timestamping is enabled.
        """
        self._timestampLog = timestamp

    def read(self):
        """Reads incoming data. Blocks until done. Calls self.disconnected(self) if appropriate."""
        print "In read..."
        try: 
            received = self._read(BLOCK_SIZE)
        except: 
            received = ''
        print "In read...2",received
        while select([self._reader],[],[],0)[0]:
        
            add = self._read(BLOCK_SIZE)
            print add,"while"    
            received +=add
            if not add: break

        if len(received): # length of 0 means disconnect
            self.DEBUG("got data " + received , DBG_XML_RAW )
            self.log(received, 'RECV:')
        else: 
            self.disconnected(self)
        return received

    def write(self,raw_data):
        """Writes raw outgoing data. Blocks until done.
           If supplied data is not unicode string, ENCODING
           is used for convertion. Avoid this!
           Always send your data as a unicode string."""
        if type(raw_data) == type(''):
            self.DEBUG('Non-utf-8 string "%s" passed to Stream.write! Treating it as %s encoded.'%(raw_data,ENCODING))
            raw_data = unicode(raw_data,ENCODING)
        data_out = raw_data.encode('utf-8')
        try:
            self._write(data_out)
            self.log(data_out, 'SENT:')
            self.DEBUG("sent %s" % data_out,DBG_XML_RAW)
        except:
            self.DEBUG("xmlstream write threw error",DBG_CONN_ERROR)
            self.disconnected(self)

    def process(self, timeout=0):
        """Receives incoming data (if any) and processes it.
           Waits for data no more than timeout seconds."""
        print "Processing1"
        if select([self._reader],[],[],timeout)[0]:
            data = self.read()
            print "data:::",data
            self._parser.Parse(data)
        print "Processing2"
        return len(data)
        print "ProcessingReturn"
        return '0'     # Zero means that nothing received but link is alive.

    def disconnect(self):
        """Close the stream and socket"""
        self.write ( u"</stream:stream>" )
        while self.process(): pass
        self._sock.close()
        self._sock = None

    def disconnected(self,conn):
        """Called when a Network Error or disconnection occurs."""
        print "Disconnected."
        try: self.disconnectHandler(conn)
        except TypeError: self.disconnectHandler()

    def disconnectHandler(self,conn): ## To be overidden ##
        """Called when a Network Error or disconnection occurs.
        Designed to be overidden"""
        raise error("Standart disconnectionHandler called. Replace it with appropriate for your client.")

    def log(self, data, inout=''):
        """Logs data to the specified filehandle. Data is time stamped
        and prefixed with inout"""
        if self._logFH is not None:
            if self._timestampLog:
                self._logFH.write("%s - %s - %s\n" % (time.asctime(), inout, data))
            else:
                self._logFH.write("%s - %s\n" % (inout, data ) )
            self._logFH.flush()

    def getIncomingID(self):
        """Returns the streams ID"""
        return self._incomingID

    def getOutgoingID(self):
        """Returns the streams ID"""
        return self._incomingID


class Client(Stream):

    def __init__(self, host, port, namespace,
                 debug=[DBG_ALWAYS],
                 log=None,
                 sock=None,
                 id=None,
                 connection=TCP,
                 hostIP=None,
                 proxy=None):

        Stream.__init__(self, namespace, debug, log, id)

        self._host = host
        self._port = port
        self._sock = sock
        self._connection = connection
        if hostIP: self._hostIP = hostIP
        else: self._hostIP = host
        self._proxy = proxy

        self._sslObj    = None
        self._sslIssuer = None
        self._sslServer = None

    def getSocket(self):
        return self._sock

    def connect(self):
        """Attempt to connect to specified host"""

        self.DEBUG("client connect called to %s %s type %i" % (self._host,
                                                               self._port,
                                                               self._connection), DBG_INIT )
        Stream.connect(self)

        ## TODO: check below that stdin/stdout are actually open
        if self._connection == STDIO:
            self._setupComms()
            return

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._proxy: self._sock.connect((self._proxy['host'], self._proxy['port']))
            else: self._sock.connect((self._hostIP, self._port))
        except socket.error, e:
            self.DEBUG("socket error: "+str(e),DBG_CONN_ERROR)
            raise

        if self._connection == TCP_SSL:
            try:
                self.DEBUG("Attempting to create ssl socket",DBG_INIT)
                self._sslObj    = socket.ssl( self._sock, None, None )
                self._sslIssuer = self._sslObj.issuer()
                self._sslServer = self._sslObj.server()
            except:
                self.DEBUG("Socket Error: No SSL Support",DBG_CONN_ERROR)
                raise

        self._setupComms()

        if self._proxy:
            self.DEBUG("Proxy connected",DBG_INIT)
            if self._proxy.has_key('type'): type = self._proxy['type'].upper()
            else: type = 'CONNECT'
            connector = []
            if type == 'CONNECT':
                connector.append(u'CONNECT %s:%s HTTP/1.0'%(self._hostIP,self._port))
            elif type == 'PUT':
                connector.append(u'PUT http://%s:%s/ HTTP/1.0'%(self._hostIP,self._port))
            else:
                self.DEBUG("Proxy Error: unknown proxy type",DBG_CONN_ERROR)
                raise error('Unknown proxy type: '+type)
            connector.append('Proxy-Connection: Keep-Alive')
            connector.append('Pragma: no-cache')
            connector.append('Host: %s:%s'%(self._hostIP,self._port))
            connector.append('User-Agent: Jabberpy/'+VERSION)
            if self._proxy.has_key('user') and self._proxy.has_key('password'):
                credentials = '%s:%s'%(self._proxy['user'],self._proxy['password'])
                credentials = encodestring(credentials).strip()
                connector.append('Proxy-Authorization: Basic '+credentials)
            connector.append('\r\n')
            bak = self._read , self._write
            self.write('\r\n'.join(connector))
            reply = self.read().replace('\r','')
            self._read , self._write = bak
            try: proto,code,desc=reply.split('\n')[0].split(' ',2)
            except: raise error('Invalid proxy reply')
            if code<>'200': raise error('Invalid proxy reply: %s %s %s'%(proto,code,desc))
            while reply.find('\n\n') == -1: reply += self.read().replace('\r','')

        self.DEBUG("Jabber server connected",DBG_INIT)
        self.header()

    def _setupComms(self):
        if self._connection == TCP:
            self._read = self._sock.recv
            self._write = self._sock.sendall
            self._reader = self._sock
        elif self._connection == TCP_SSL:
            self._read = self._sslObj.read
            self._write = self._sslObj.write
            self._reader = self._sock
        elif self._connection == STDIO:
            self._read = self.stdin.read
            self._write = self.stdout.write
            self._reader = sys.stdin
        else:
            self.DEBUG('unknown connection type',DBG_CONN_ERROR)
            raise IOError('unknown connection type')

class Server:

    def now(self): return time.ctime(time.time())

    def __init__(self, maxclients=10):

        self.host = ''
        self.port = 5222
        self.streams = []

        # make main sockets for accepting new client requests
        self.mainsocks, self.readsocks, self.writesocks = [], [], []

        self.portsock = socket(AF_INET, SOCK_STREAM)
        self.portsock.bind((self.host, self.port))
        self.portsock.listen(maxclients)

        self.mainsocks.append(self.portsock)  # add to main list to identify
        self.readsocks.append(self.portsock)  # add to select inputs list

        # event loop: listen and multiplex until server process killed


    def serve(self):

        print 'select-server loop starting'

        while 1:
            print "LOOPING"
            readables, writeables, exceptions = select(self.readsocks,
                                                       self.writesocks, [])
            for sockobj in readables:
                if sockobj in self. mainsocks:   # for ready input sockets
                    newsock, address = sockobj.accept() # accept not block
                    print 'Connect:', address, id(newsock)
                    self.readsocks.append(newsock)
                    self._makeNewStream(newsock)
                    # add to select list, wait
                else:
                    # client socket: read next line
                    data = sockobj.recv(1024)
                    # recv should not block
                    print '\tgot', data, 'on', id(sockobj)
                    if not data:        # if closed by the clients
                        sockobj.close() # close here and remv from
                        self.readsocks.remove(sockobj)
                    else:
                    # this may block: should really select for writes too
                        sockobj.send('Echo=>%s' % data)

    def _makeNewStream(self, sckt):
        new_stream = Stream('localhost', 5222,
                            'jabber:client',
                            sock=sckt)
        self.streams.append(new_stream)
                            ## maybe overide for a 'server stream'
        new_stream.header()
        return new_stream

    def _getStreamSockets(self):
        socks = [];
        for s in self.streams:
            socks.append(s.getSocket())
        return socks

    def _getStreamFromSocket(self, sock):
        for s in self.streams:
            if s.getSocket() == sock:
                return s
        return None
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

