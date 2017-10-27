# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'purchase_order': [
        ('state', None, None),
    ],
}

def map_order_state(cr):
    """ Map values for state field in purchase.order and purchase.order.line.
    Do this in the pre script because it influences the automatic calculation
    of the computed fields wrt. invoicing """
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state',
        [('approved', 'purchase'), ('bid', 'sent'),
         ('confirmed', 'to approve'), ('draft', 'draft'),
         ('except_invoice', 'purchase'), ('except_picking', 'purchase')],
        table='purchase_order')

    cr.execute("""
        UPDATE purchase_order_line l
        SET state = o.state
        FROM purchase_order o
        WHERE l.order_id = o.id""")

def backup_fields_purchase_order(cr):
    '''
    Metodo para respaldar campos funcionales de la tabla purchase_order
    '''
    column_copies_po = {
                    'purchase_order': [
                        ('amount_without_service', None, None),
                        ('amount_tax', None, None),
                        ('amount_total', None, None),
                        ('amount_untaxed', None, None),
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_po)

def backup_fields_purchase_order_line(cr):
    '''
    Metodo para respaldar campos funcionales de la tabla purchase_order_line
    '''
    column_copies_pol = {
                    'purchase_order_line': [
                        ('price_unit', None, None),    
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_pol)

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    map_order_state(cr)
    backup_fields_purchase_order(cr)
    backup_fields_purchase_order_line(cr)
    