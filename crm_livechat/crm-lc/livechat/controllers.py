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

