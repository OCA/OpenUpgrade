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

from openupgrade import openupgrade

@openupgrade.migrate()
def migrate(cr, version):
    cr.execute('''
      update membership_membership_line set 
        membership_id=(select product_id 
          from account_invoice_line 
          where id=account_invoice_line), 
        member_price=(select price_subtotal 
          from account_invoice_line 
          where id=account_invoice_line),
        date=create_date''')
