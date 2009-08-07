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
import tools

class Currency(osv.osv):
    _inherit = "res.currency"
    _columns = {
        'company_id':fields.many2one('res.company', 'Company'),
        'date': fields.date('Date'),
        'base': fields.boolean('Base')
    }
    
    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        res=super(osv.osv, self).read(cr, user, ids, fields, context, load)
        for r in res:
            if r.__contains__('rate_ids'):
                rates=r['rate_ids']
                if rates:
                    currency_rate_obj=self.pool.get('res.currency.rate')
                    currency_date=currency_rate_obj.read(cr,user,rates[0],['name'])['name']
                    r['date']=currency_date
        return res
        
        
Currency()

class Company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'currency_ids': fields.one2many('res.currency', 'company_id', 'Currency')
    }
Company()