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
import time
import netsvc
from osv import fields,osv,orm
import ir
from mx import DateTime


class edi_log(osv.osv):
    _name = "edi.log"
    _description = "EDI log"
    _columns = {    'name': fields.char('Log name', size=32, required=True),
                    'log_line': fields.one2many('edi.log.line', 'log_id', 'Log Lines', readonly=True, states={'draft':[('readonly', False)]}),
                }

    _defaults = {   'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                }

edi_log()


class edi_log_line(osv.osv):
    _name = "edi.log.line"
    _description = "EDI Log Line"
    _columns = {    'log_id': fields.many2one('edi.log', 'Log Ref'),
                    'name': fields.char('Name', size=64, required=True),
                    'logdesc': fields.text('Description'),
                    'sender': fields.many2one('res.partner', 'Partner', readonly=True),
                    'timestamp': fields.char('Order date', size=13),
                    'order_num': fields.char('Edi Order Id', size=15),
                }
    _defaults = {   'name': lambda *a: 'logline',
                }

edi_log_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

