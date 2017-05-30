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
    'res_partner': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
    'res_country': [
        ('image', None),
    ],
    'ir_ui_menu': [
        ('web_icon_data', None),
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
            ('contacts', 'mail'),
            ('marketing_crm', 'crm'),
            ('web_gantt', 'web'),
            ('web_graph', 'web'),
            ('web_kanban_sparkline', 'web'),
            ('web_tests', 'web'),
            ('website_report', 'report'),
            # from OCA/account-financial-tools - Features changed
            ('account_move_line_no_default_search', 'account'),
            ('account_tax_chart_interval', 'account'),
            # from OCA/server-tools - features included now in core
            ('base_concurrency', 'base'),
            ('base_debug4all', 'base'),
            ('cron_run_manually', 'base'),
            ('shell', 'base'),
            # from OCA/social - included in core
            ('website_mail_snippet_table_edit', 'mass_mailing'),
            ('mass_mailing_sending_queue', 'mass_mailing'),
            # from OCA/crm - included in core
            ('crm_lead_lost_reason', 'crm'),
            # from OCA/sale-workflow - included in core
            ('sale_order_back2draft', 'sale'),
            # from OCA/bank-payment
            ('account_payment_sale_stock', 'account_payment_sale'),
            # from OCA/website
            ('website_event_register_free', 'website_event'),
            ('website_event_register_free_with_sale', 'website_event_sale'),
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
