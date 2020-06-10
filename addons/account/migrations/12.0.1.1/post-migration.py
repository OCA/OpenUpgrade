# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def disable_account_payment_term_comp_rule(env):
    # This rule is disabled (active=False), because if not, when migrating
    # we will get missing payment terms in a multi-company environment
    # (as previously there wasn't a record rule).
    payment_rule = env.ref('account.account_payment_term_comp_rule')
    payment_rule.active = False


def map_account_journal_bank_statements_source(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('bank_statements_source'),
        'bank_statements_source',
        [('manual', 'undefined'),
         ],
        table='account_journal', write='sql')


def map_account_payment_term_line_option(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE account_payment_term_line
        SET days = 31
        WHERE option IN ('last_day_following_month', 'last_day_current_month')
        """
    )
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('option'),
        'option',
        [('fix_day_following_month', 'after_invoice_month'),
         ('last_day_following_month', 'day_following_month'),
         ('last_day_current_month', 'day_current_month'),
         ],
        table='account_payment_term_line', write='sql')


def map_account_tax_type_tax_use(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE account_tax
        SET type_tax_use = 'adjustment'
        WHERE type_tax_use = 'none' AND %s = TRUE
        """, (AsIs(openupgrade.get_legacy_name('tax_adjustment')), ),
    )
    openupgrade.logged_query(
        cr, """
        UPDATE account_tax_template
        SET type_tax_use = 'adjustment'
        WHERE type_tax_use = 'none' AND %s = TRUE
        """, (AsIs(openupgrade.get_legacy_name('tax_adjustment')), ),
    )


def fill_account_chart_template_account_code_prefix(cr):
    # if company_id was filled:
    openupgrade.logged_query(
        cr, """
        UPDATE account_chart_template act
        SET bank_account_code_prefix = rc.bank_account_code_prefix
        FROM res_company rc
        WHERE act.%s = rc.id AND act.bank_account_code_prefix IS NULL
        """, (AsIs(openupgrade.get_legacy_name('company_id')), ),
    )
    openupgrade.logged_query(
        cr, """
        UPDATE account_chart_template act
        SET cash_account_code_prefix = rc.cash_account_code_prefix
        FROM res_company rc
        WHERE act.%s = rc.id AND act.cash_account_code_prefix IS NULL
        """, (AsIs(openupgrade.get_legacy_name('company_id')), ),
    )
    # if company_id was not filled:
    openupgrade.logged_query(
        cr, """
        UPDATE account_chart_template act
        SET bank_account_code_prefix = 'OUB'
        WHERE act.bank_account_code_prefix IS NULL
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE account_chart_template act
        SET cash_account_code_prefix = 'OUB'
        WHERE act.cash_account_code_prefix IS NULL
        """
    )
    # transfer_account_code_prefix:
    openupgrade.logged_query(
        cr, """
        UPDATE account_chart_template act
        SET transfer_account_code_prefix = trim(trailing '0' from aat.code)
        FROM account_account_template aat
        WHERE act.%s = aat.id
        """, (AsIs(openupgrade.get_legacy_name('transfer_account_id')), ),
    )
    openupgrade.logged_query(
        cr, """
        UPDATE res_company rc
        SET transfer_account_code_prefix = act.transfer_account_code_prefix
        FROM account_chart_template act
        WHERE act.%s = rc.id
        """, (
            AsIs(openupgrade.get_legacy_name('company_id')),
        ),
    )


def update_res_company_account_helper_states(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE res_company
        SET account_dashboard_onboarding_state = 'done',
            account_invoice_onboarding_state = 'done',
            account_onboarding_invoice_layout_state = 'done',
            account_onboarding_sale_tax_state = 'done',
            account_onboarding_sample_invoice_state = 'done'
        """
    )


def update_res_company_account_setup_steps_states(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE res_company
        SET account_setup_bank_data_state = 'done'
        WHERE account_setup_bank_data_done = TRUE
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE res_company
        SET account_setup_fy_data_state = 'done'
        WHERE account_setup_fy_data_done = TRUE
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE res_company
        SET account_setup_coa_state = 'done'
        WHERE account_setup_coa_done = TRUE
        """
    )


def fill_account_journal_alias_id(env):
    journal_model = env["account.journal"]
    journals = journal_model.with_context(
        active_test=False).search([('type', '=', 'purchase')])
    for journal in journals:
        journal._update_mail_alias({})


def fill_account_move_reverse_entry_id(env):
    AccountMove = env['account.move']
    if openupgrade.table_exists(env.cr, 'account_move_reverse'):
        reversal_moves = AccountMove.search([
            ('auto_reverse', '=', True),
            ('reverse_entry_id', '=', False),
        ])
        reversal_moves.write({'reverse_date': '2999-12-31'})
        env['ir.filters'].create({
            'name': 'To be reversed (undetermined date)',
            'model_id': 'account.move',
            'domain': "[('auto_reverse', '=', True),"
                      "('reverse_entry_id', '=', False),"
                      "('reverse_date', '=', '2999-12-31')]",
        })
    domain = [('reverse_entry_id', '=', False)]
    installed_langs = env['res.lang'].search([])  # search only active
    for lang in installed_langs:
        reversal_text = env['ir.translation']._get_source(
            name=False, types='code', lang=lang.code,
            source='reversal of: ')
        reversal_moves = AccountMove.search(
            domain + [('ref', '=like', '%s%%' % reversal_text)]
        )
        for move in reversal_moves:
            name = move.ref.partition(reversal_text)[2]
            origin = AccountMove.search([('name', '=', name)], limit=1)
            if origin and not origin[0].reverse_entry_id:
                origin[0].reverse_entry_id = move.id


def recompute_invoice_taxes_add_analytic_tags(env):
    analytic_taxes = env['account.tax'].search([('analytic', '=', True)])
    taxes = env['account.tax'].search([
        ('children_tax_ids', 'in', analytic_taxes.ids),
    ]) | analytic_taxes
    invoice_lines = env['account.invoice.line'].search(
        [('invoice_line_tax_ids', 'in', taxes.ids)])
    invoices = invoice_lines.mapped('invoice_id')
    for invoice in invoices:
        amount_total = invoice.amount_total
        with env.cr.savepoint():
            invoice.compute_taxes()
            if invoice.amount_total != amount_total:
                env.cr.rollback()


def set_default_taxes(env):
    IrDefault = env['ir.default']
    for company in env['res.company'].search([]):
        stax = IrDefault.get(
            'product.template', "taxes_id", company_id=company.id,
        )
        ptax = IrDefault.get(
            'product.template', "supplier_taxes_id", company_id=company.id,
        )
        company.write({
            'account_sale_tax_id': stax[0] if stax else False,
            'account_purchase_tax_id': ptax[0] if ptax else False,
        })


def populate_fiscal_years(env):
    if openupgrade.table_exists(env.cr, 'account_fiscalyear'):
        # An old 8.0 table is still present with fiscal years
        # We populate the new table with the old values
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_fiscal_year (
                id, name, company_id, date_from, date_to,
                create_date, create_uid, write_date, write_uid
            )
            SELECT
                id, name, company_id, date_start, date_stop,
                create_date, create_uid, write_date, write_uid
            FROM account_fiscalyear;
            """)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    disable_account_payment_term_comp_rule(env)
    map_account_journal_bank_statements_source(cr)
    map_account_payment_term_line_option(cr)
    map_account_tax_type_tax_use(cr)
    env['account.group']._parent_store_compute()
    fill_account_chart_template_account_code_prefix(cr)
    update_res_company_account_helper_states(cr)
    update_res_company_account_setup_steps_states(cr)
    fill_account_journal_alias_id(env)
    fill_account_move_reverse_entry_id(env)
    recompute_invoice_taxes_add_analytic_tags(env)
    set_default_taxes(env)
    populate_fiscal_years(env)
    openupgrade.load_data(
        cr, 'account', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        cr, 'account', [
            'mail_template_data_payment_receipt',
            'email_template_edi_invoice',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'account.mail_template_data_notification_email_account_invoice',
        ],
    )
