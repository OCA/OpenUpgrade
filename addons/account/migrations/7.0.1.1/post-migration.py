# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
import logging
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_70

logger = logging.getLogger('OpenUpgrade')

def migrate_invoice_addresses(cr, pool):
    # Contact id takes precedence over old partner id
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.invoice',
        'partner_id', openupgrade.get_legacy_name('address_contact_id'))
    # Invoice id takes precedence over contact id
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.invoice',
        'partner_id', openupgrade.get_legacy_name('address_invoice_id'))

def migrate_invoice_names(cr, pool):
    """
    Join existing char values and obsolete note values into
    new text field name on the invoice line.
    """
    invoice_line_obj = pool.get('account.invoice.line')
    
    cr.execute("""
        SELECT id, {0}, {1}
        FROM account_invoice_line
        WHERE {1} is not NULL AND {1} != ''
        """.format(
            'name',
            openupgrade.get_legacy_name('note')))
    for (invoice_line_id, name, note) in cr.fetchall():
        name = name + '\n' if name else ''
        invoice_line_obj.write(
            cr, SUPERUSER_ID, [invoice_line_id],
            {'name': name + note})

def lock_closing_reconciliations(cr, pool):
    """
    Reconciliations on closing entries are now locked
    for deletion. Therefore, lock existing closing entries.
    """
    fiscalyear_obj = pool.get('account.fiscalyear')
    period_obj = pool.get('account.period')
    move_line_obj = pool.get('account.move.line')
    reconcile_obj = pool.get('account.move.reconcile')
    for fiscalyear_id in fiscalyear_obj.search(
            cr, SUPERUSER_ID, []):
        move_line_ids = move_line_obj.search(
            cr, SUPERUSER_ID,
            [('period_id.special', '=', True),
             ('period_id.fiscalyear_id', '=', fiscalyear_id)])
        reconcile_ids = reconcile_obj.search(
            cr, SUPERUSER_ID,
            [('line_id', 'in', move_line_ids)])
        reconcile_obj.write(
            cr, SUPERUSER_ID, reconcile_ids,
            {'opening_reconciliation': True})

def migrate_payment_term(cr, pool):
    partner_obj = pool.get('res.partner')
    field_id = pool.get('ir.model.fields').search(
        cr, SUPERUSER_ID, [
            ('name', '=', 'property_supplier_payment_term'),
            ('model', '=', 'res.partner'),
            ])[0]
          
    cr.execute(
        """
        SELECT company_id, value_reference, res_id
        FROM ir_property
        WHERE name = 'property_payment_term'
        AND res_id like 'res.partner,%'
        """)
    for row in cr.fetchall():
        if partner_obj.read(
                cr, SUPERUSER_ID, int(row[2][12:]), ['supplier']
                )['supplier']:
            cr.execute(
                """
                INSERT INTO ir_property (
                    create_uid,
                    create_date,
                    name,
                    type,
                    company_id,
                    fields_id,
                    value_reference,
                    res_id)
                VALUES(
                    %s,
                    CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
                    'property_supplier_payment_term',
                    'many2one',
                    %s,
                    %s,
                    %s,
                    %s)
                """, (SUPERUSER_ID, row[0], field_id, row[1], row[2]))
        
def merge_account_cashbox_line(cr, pool):
    # Check an unmanaged case by the migration script
    cr.execute("""
        select count(*) as quantity2 from (
        SELECT count(*) as quantity1
        FROM account_cashbox_line
        GROUP BY %s, %s, pieces) as tmp
        WHERE quantity1 > 1
        """%(
            openupgrade.get_legacy_name('starting_id'), 
            openupgrade.get_legacy_name('ending_id'), 
            ))
    count = cr.fetchone()[0]
    if count>0:
        logger.error('Some duplicated datas in account_cashbox_line (%s). This case is not covered.' %(count))

    cashboxline_obj = pool.get('account.cashbox.line')
    # Getting all the row from cashbox_line (type "ending")
    cr.execute("""
        SELECT id as id_end, pieces, %s as ending_id, %s as number
        FROM account_cashbox_line 
        WHERE %s is not NULL AND bank_statement_id is NULL
        """ %(
            openupgrade.get_legacy_name('ending_id'), 
            openupgrade.get_legacy_name('number'), 
            openupgrade.get_legacy_name('ending_id'), 
            ))
    for (id_end, pieces, ending_id, number) in cr.fetchall():
        # Check if there is some corresping cashbox_line (type "starting") 
        cr.execute("""
            SELECT id, %s
            FROM account_cashbox_line
            WHERE %s=%s AND pieces=%s
            """ %(
                openupgrade.get_legacy_name('number'),
                openupgrade.get_legacy_name('starting_id'),
                ending_id,
                pieces,
                ))

        if cr.rowcount==0: 
            # "ending" cashbox_line becomes normal.
            cashboxline_obj.write(
                cr, SUPERUSER_ID, [id_end],
                {
                    'number_opening': 0,
                    'number_closing': number,
                    'bank_statement_id': ending_id,
                })

        elif cr.rowcount==1:
            row = cr.fetchone()
            # "starting" cashbox_line becomes normal with data of "ending" cashbox_line
            cashboxline_obj.write(
                cr, SUPERUSER_ID, [row[0]],
                {
                    'number_opening': row[1],
                    'number_closing': number,
                    'bank_statement_id': ending_id,
                })
            # delete the "ending" cashbox_line
            cashboxline_obj.unlink(cr, SUPERUSER_ID, [id_end])
            
        elif cr.rowcount>1:
            # there is duplicated datas in the 6.1 Database
            pass

    # Getting all the rows from cashbox_line (type "starting") that didn't change
    cr.execute("""
        SELECT id as id_start, %s as starting_id, %s as number
        FROM account_cashbox_line 
        WHERE %s is not NULL AND bank_statement_id is NULL
        """ %(
            openupgrade.get_legacy_name('starting_id'), 
            openupgrade.get_legacy_name('number'), 
            openupgrade.get_legacy_name('starting_id'), 
            ))

    for (id_start, starting_id, number) in cr.fetchall():
        cashboxline_obj.write(
            cr, SUPERUSER_ID, [id_start],
            {
                'number_opening': number,
                'number_closing': 0,
                'bank_statement_id': starting_id,
            })


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_invoice_addresses(cr, pool)
    migrate_invoice_names(cr, pool)
    lock_closing_reconciliations(cr, pool)
    migrate_payment_term(cr, pool)
    merge_account_cashbox_line(cr, pool)
    openupgrade.load_xml(
        cr, 'account',
        'migrations/7.0.1.1/data.xml')
