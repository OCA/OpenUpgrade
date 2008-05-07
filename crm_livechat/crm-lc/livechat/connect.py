from twisted.words.protocols import jabber
from twisted.xish import xmlstream
from twisted.words.protocols.jabber import client, jid
from twisted.internet import reactor, defer

class Connection:
    
    def __init__(self, who, myjid):
        self.jid = jid.JID(myjid)
        self.who = who

    def connect(self, passwd, port=5223):
        self.factory = client.jabberClientFactory(self.jid, passwd)
        
        self.factory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT,self.onAuthSuccess)
        self.factory.addBootstrap(client.XMPPAuthenticator.AUTH_FAILED_EVENT,self.onAuthFailed)
        
        self.connector = reactor.connectTCP(self.jid.host, port, self.factory)
    
    def onAuthSuccess(self, stream):
        print "%s: Successful connection" % (self.who)
        self.stream = stream

    def onAuthFailed(self, stream):
        print "%s: Failed connection" % (self.who)
        self.factory.stopTrying()
        self.connector.disconnect()

c1 = Connection('1', 'cza@tinyerp.com')
c1.connect('cza')

reactor.run()
