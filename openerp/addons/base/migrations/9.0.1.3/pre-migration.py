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
        cr, [
            ('account_chart', 'account'),
            ('account_followup', 'account_credit_control'),
            ('contacts', 'mail'),
            ('marketing_crm', 'crm'),
            ('email_template', 'mail'),  # mail_template class
            ('procurement_jit_stock', 'procurement_jit'),
            ('web_gantt', 'web'),
            ('web_graph', 'web'),
            ('web_kanban_sparkline', 'web'),
            ('web_tests', 'web'),
            ('website_report', 'report'),
            # from OCA/account-financial-tools - Features changed
            ('account_move_line_no_default_search', 'account'),
            ('account_tax_chart_interval', 'account'),
            # from OCA/account-financial-reporting
            ('account_journal_report_xls', 'account_journal_report'),
            ('account_financial_report_webkit_xls',
             'account_financial_report_qweb'),
            ('account_tax_report_no_zeroes', 'account'),
            # from OCA/account_payment
            ('account_payment_term_multi_day',
             'account_payment_term_extension'),
            # from OCA/bank-statement-reconcile
            ('account_easy_reconcile', 'account_mass_reconcile'),
            ('account_advanced_reconcile', 'account_mass_reconcile'),
            ('account_bank_statement_period_from_line_date', 'account'),
            # from OCA/connector-telephony
            ('asterisk_click2dial_crm', 'crm_phone'),
            # from OCA/server-tools - features included now in core
            ('base_concurrency', 'base'),
            ('base_debug4all', 'base'),
            ('cron_run_manually', 'base'),
            ('shell', 'base'),
            # from OCA/social - included in core
            ('website_mail_snippet_table_edit', 'mass_mailing'),
            ('mass_mailing_sending_queue', 'mass_mailing'),
            ('website_mail_snippet_bg_color',
             'web_editor_background_color'),  # this one now located in OCA/web
            # from OCA/crm - included in core
            ('crm_lead_lost_reason', 'crm'),
            # from OCA/sale-workflow - included in core
            ('account_invoice_reorder_lines', 'account'),
            ('sale_order_back2draft', 'sale'),
            ('partner_prepayment', 'sale_delivery_block'),
            ('sale_fiscal_position_update', 'sale'),
            ('sale_documents_comments', 'sale_comment_propagation'),
            # from OCA/bank-payment
            ('account_payment_sale_stock', 'account_payment_sale'),
            # from OCA/website
            ('website_event_register_free', 'website_event'),
            ('website_event_register_free_with_sale', 'website_event_sale'),
            ('website_sale_collapse_categories', 'website_sale'),
            # OCA/reporting-engine
            ('report_xls', 'report_xlsx'),
            # OCA/l10n-spain
            ('l10n_es_account_financial_report', 'account_journal_report'),
            # OCA/stock-logistics-workflow
            ('stock_dropshipping_dual_invoice', 'stock_dropshipping'),
        ], merge_modules=True,
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
