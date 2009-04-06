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
class etl_component_control_sleep(osv.osv):
    _name='etl.component'
    _inherit = 'etl.component'
    _columns={
        'delay' :  fields.float('Delay'),
    }
    _defaults={
            'delay':lambda *x:'1'
    }

    def create_instance(self, cr, uid, id, context={}, data={}):
        val=super(etl_component_control_sleep, self).create_instance(cr, uid, id, context, data)
        cmp=self.browse(cr, uid, id)
        if cmp.type_id.name == 'control.sleep':
            val = etl.component.control.sleep(cmp.delay)
        return val

etl_component_control_sleep()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: