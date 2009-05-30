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

from osv import fields,osv
from tools import config

class res_partner_turnover(osv.osv):
    _description='Partner turnover'
    _name = 'res.partner.turnover'
    _columns = {
        'name': fields.char('Period', size=32),
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='cascade'),
        'turnover': fields.float('Turn over (Value)', digits=(16, int(config['price_accuracy']))),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'manpower': fields.float('Manpower'),
    }
res_partner_turnover()

class res_partner(osv.osv):
    _description='The partner object'
    _inherit = "res.partner"
    _columns = {
        'turnover_id': fields.one2many('res.partner.turnover', 'partner_id', 'Turnover'),
    }
    _defaults = {
        'turnover_id': lambda *a: False
    }
res_partner()