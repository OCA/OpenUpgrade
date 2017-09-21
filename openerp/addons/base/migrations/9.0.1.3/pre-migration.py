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

column_renames = {
    'res_partner_bank': [
        ('bank', 'bank_id'),
    ],
}


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
             'web_editor_background_color'), # this one now located in OCA/web
            # from OCA/crm - included in core
            ('crm_lead_lost_reason', 'crm'),
            # from OCA/sale-workflow - included in core
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


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_columns(cr, column_renames)
    remove_obsolete(cr)
    pre_create_columns(cr)
    cleanup_modules(cr)
    map_res_partner_type(cr)


def pre_create_columns(cr):
    openupgrade.logged_query(cr, """
        alter table ir_model_fields add column compute text""")
