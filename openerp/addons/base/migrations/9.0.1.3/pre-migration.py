# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2015-Today: Odoo Community Association
#    @author: Stephane LE CORNEC
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

from openupgradelib import openupgrade


column_copies = {
    'ir_act_url': [
        ('help', None, None),
    ],
    # 'ir_act_window': [
    #     ('help', None, None),
    # ],
    'ir_actions': [
        ('help', None, None),
    ],
    # 'ir_act_client': [
    #     ('help', None, None),
    # ],
    'ir_act_report_xml': [
        ('help', None, None),
    ],
    'ir_act_server': [
        ('help', None, None),
    ],
    'ir_ui_view': [
        ('arch', 'arch_db', None),
    ],
}

column_renames = {
    'res_partner_bank': [
        ('bank', 'bank_id'),
    ],
}

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_columns(cr, column_renames)
    # purchase double validation migraion
    cr.execute("""
    select condition from wkf_transition wkf join ir_model_data ir 
    on wkf.id = ir.res_id and ir.name = 'trans_confirmed_double_gt' 
    and ir.module = 'purchase_double_validation'
    """)
#    amount = cr.dictfetchone()
#    double_validation_amount = str(amount['condition']).split(" ")[-1]

    # delete purchase order workflow
    openupgrade.delete_model_workflow(cr, 'purchase.order')
#    transitions = openupgrade.deactivate_workflow_transitions(cr, 'purchase.order')
#    openupgrade.reactivate_workflow_transitions(cr, transitions)

    # Inherited Views that encountered errors while running the migration.
    cr.execute("""
        UPDATE ir_ui_view
        SET active = FALSE
        WHERE name in ('res.partner.view.address_type', 'crm settings',
        'partner.view.button.journal_item_count','res.partner.stock.property.form.inherit',
        'res.users.form.hr')
    """)
    cr.execute("""
        UPDATE ir_ui_view SET active=false WHERE inherit_id in 
        (SELECT id FROM ir_ui_view WHERE name in 
        ('res.partner.view.address_type','crm settings',
        'partner.view.button.journal_item_count'))
    """)
