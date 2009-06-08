#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import etl
import tools
from osv import osv, fields

class gdoc_connector(osv.osv):
    _name = 'etl.connector'
    _inherit = 'etl.connector'

    def create_instance(self, cr, uid, id , context={}, data={}):
        val =  super(gdoc_connector, self).create_instance(cr, uid, id, context, data)
        con = self.browse(cr, uid, id)
        if con.type == 'gdoc':
            val =  etl.connector.gcalendar_connector(con.uid, con.passwd, con.delay, con.name)
        return val

gdoc_connector()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
