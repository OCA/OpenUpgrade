# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 SISTHEO. All Rights Reserved
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

from mx import DateTime
import time

from osv import fields, osv
import pooler


class account_generation_config(osv.osv):
    _name        = "account.generation.config"
    _description = "Account Generation Configuration"
    _columns = {
                'name':fields.char('Configuration Name',size=64,required=True,translate=True),
                'customer':fields.many2one('account.account','Global Customer'),
                'supplier':fields.many2one('account.account','Global Supplier'),
                'nbcar':fields.integer('Char size', help="Number of character for the creation of accounts"),
            }
    _defaults = {
            'nbcar': lambda *a:3,
            'name': lambda *a:'default',
        }
account_generation_config()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
