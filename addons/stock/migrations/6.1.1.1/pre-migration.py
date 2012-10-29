# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade

def update_wkf_items(cr):
    """ 
    Replace references to act_cancel_inv with
    references to act_cancel in workflow workitems
    """
    openupgrade.logged_query(cr, """
            UPDATE wkf_workitem
            SET act_id = (
                SELECT res_id FROM ir_model_data
                WHERE module = 'stock'
                AND name = 'act_cancel')
            WHERE act_id = (
                SELECT res_id FROM ir_model_data
                WHERE module = 'stock'
                AND name = 'act_cancel_inv')
    """)

@openupgrade.migrate()
def migrate(cr, version):
    update_wkf_items(cr)
