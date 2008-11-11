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
import math
from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
    _name = "res.partner"
    _description = "Sale agent sale info"
    _inherit="res.partner"
    _columns = {
                #'agent_id': fields.one2many('sale.agent','partner_id','salesagent', required=True),
                  'agent_id': fields.many2one('sale.agent','Sale Agent'),
                  #'agent_rate': fields.float('Commission rate of Agent'),
                }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

