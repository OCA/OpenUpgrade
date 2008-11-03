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

from osv import osv, fields

class account_journal(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_journal()

class account_analytic_journal(osv.osv):
    _name = "account.analytic.journal"
    _inherit = "account.analytic.journal"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_analytic_journal()

class account_budget_post(osv.osv):
    _name = 'account.budget.post'
    _inherit = 'account.budget.post'
    _columns ={
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_budget_post()

class account_period(osv.osv):
    _name = 'account.period'
    _inherit = 'account.period'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_period()

class account_fiscalyear(osv.osv):
    _name = 'account.fiscalyear'
    _inherit = 'account.fiscalyear'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
account_fiscalyear()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

