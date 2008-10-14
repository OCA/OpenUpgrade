# -*- encoding: utf-8 -*-
from turbogears import controllers, expose, flash, redirect, config
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


cnhost = config.get('cnhost', path="crm")
cnport = config.get('cnport', path="crm")
cntype = config.get('cntype', path="crm")

rpc.session = rpc.RPCSession( cnhost, cnport, cntype , storage=cherrypy.session)


class Root(controllers.RootController):

    chatfunc = subcontrollers.livechat.chatfunc.ChatFunc();

    @expose(template="livechat.templates.welcome")
    def index(self):
        if not(cherrypy.session.has_key(cherrypy.request.remoteAddr)):
            cherrypy.session[cherrypy.request.remoteAddr] = cherrypy.request.remoteAddr

        print "cherrypy.session[cherrypy.request.remoteAddr]::",cherrypy.session[cherrypy.request.remoteAddr],"::::",cherrypy.request.remoteAddr
        print "Redirecting to ChatFunc"
        raise redirect('chatfunc/index')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

