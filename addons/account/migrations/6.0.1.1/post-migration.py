# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
from openupgradelib import openupgrade

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'account.fiscalyear': [
        ('company_id', None),
        ],    
    'account.journal': [
        ('company_id', None),
        ],    
    'account.analytic.account': [
        ('currency_id', None),
        ],    
    'account.analytic.journal': [
        ('company_id', None),
        ],    
    'account.invoice': [
        ('user_id', None),
        ],    
    }

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, defaults)
    openupgrade.load_xml(cr, 'account', 'migrations/6.0.1.1/data.xml')
