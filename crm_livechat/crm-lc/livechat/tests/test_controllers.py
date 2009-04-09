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
import unittest
import turbogears
from turbogears import testutil
from livechat.controllers import Root
import cherrypy

cherrypy.root = Root()

class TestPages(unittest.TestCase):

    def setUp(self):
        turbogears.startup.startTurboGears()

    def tearDown(self):
        """Tests for apps using identity need to stop CP/TG after each test to
        stop the VisitManager thread. 
        See http://trac.turbogears.org/turbogears/ticket/1217 for details.
        """
        turbogears.startup.stopTurboGears()

    def test_method(self):
        "the index method should return a string called now"
        import types
        result = testutil.call(cherrypy.root.index)
        assert type(result["now"]) == types.StringType

    def test_indextitle(self):
        "The indexpage should have the right title"
        testutil.createRequest("/")
        response = cherrypy.response.body[0].lower() 
        assert "<title>welcome to turbogears</title>" in response

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

