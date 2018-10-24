# -*- coding: utf-8 -*-
# Copyright Stephane LE CORNEC
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp.addons.openupgrade_records.lib import apriori


column_copies = {
    'ir_actions': [
        ('help', None, None),
    ],
    'ir_ui_view': [
        ('arch', 'arch_db', None),
    ],
    'res_partner': [
        ('type', None, None),
    ]
}

field_renames = [
    ('res.partner.bank', 'res_partner_bank', 'bank', 'bank_id'),
    # renamings with oldname attribute - They also need the rest of operations
    ('res.partner', 'res_partner', 'ean13', 'barcode'),
]


OBSOLETE_RULES = (
    'multi_company_default_rule',
    'res_currency_rule',
)


def remove_obsolete(cr):
    openupgrade.logged_query(cr, """
        delete from ir_rule rr
        using ir_model_data d where rr.id=d.res_id
        and d.model = 'ir.rule' and d.module = 'base'
        and d.name in {}
        """.format(OBSOLETE_RULES))


def cleanup_modules(cr):
    """Don't report as missing these modules, as they are integrated in
    other modules."""
    openupgrade.update_module_names(
        cr, apriori.merged_modules, merge_modules=True,
    )


def map_res_partner_type(cr):
    """ The type 'default' is not an option in v9.
        By default we map it to 'contact'.
    """
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [('default', 'contact')],
        table='res_partner', write='sql')


def has_recurring_contracts(cr):
    """ Whether or not to migrate to the contract module """
    if openupgrade.column_exists(
            cr, 'account_analytic_account', 'recurring_invoices'):
        cr.execute(
            """SELECT id FROM account_analytic_account
            WHERE recurring_invoices LIMIT 1""")
        if cr.fetchone():
            return True
    return False


def migrate_translations(cr):
    """ Translations of field names are encoded differently in Odoo 9.0:
     version |           name                    | res_id |  type
    ---------+-----------------------------------+--------+-------
     8.0     | ir.module.module,summary          |      0 | field
     9.0     | ir.model.fields,field_description |    759 | model
    """
    openupgrade.logged_query(
        cr, """
        WITH mapping AS (
            SELECT imd.module,
                imf.model||','||imf.name AS name80,
                'ir.model.fields,field_description' AS name90,
                imd.res_id
            FROM ir_model_data imd
            JOIN ir_model_fields imf ON imf.id = imd.res_id
            WHERE imd.model = 'ir.model.fields' ORDER BY imd.id DESC)
        UPDATE ir_translation
        SET name = mapping.name90, type = 'model', res_id = mapping.res_id
        FROM mapping
        WHERE name = mapping.name80
            AND type = 'field'
            AND (ir_translation.module = mapping.module
                 OR ir_translation.module IS NULL); """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    module_renames = dict(apriori.renamed_modules)
    if not has_recurring_contracts(cr):
        # Don't install contract module without any recurring invoicing
        del module_renames['account_analytic_analysis']
    openupgrade.update_module_names(
        cr, module_renames.iteritems()
    )
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_fields(env, field_renames, no_deep=True)
    remove_obsolete(cr)
    pre_create_columns(cr)
    cleanup_modules(cr)
    map_res_partner_type(cr)
    migrate_translations(env.cr)


def pre_create_columns(cr):
    openupgrade.logged_query(cr, """
        alter table ir_model_fields add column compute text""")
