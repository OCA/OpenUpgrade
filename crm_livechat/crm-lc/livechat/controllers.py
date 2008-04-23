from turbogears import controllers, expose, flash,redirect
# from livechat import model

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.all import LegacyClientStream

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
    def chat_window(self):
        pass
        return dict()