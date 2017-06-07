# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import operator
from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager


def map_bank_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('draft', 'open')],
        table='account_bank_statement', write='sql')


def map_type_tax_use(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type_tax_use'), 'type_tax_use',
        [('all', 'none')],
        table='account_tax', write='sql')


def map_type_tax_use_template(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type_tax_use'), 'type_tax_use',
        [('all', 'none')],
        table='account_tax_template', write='sql')


def map_journal_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'type',
        [
            ('purchase_refund', 'purchase'),
            ('sale_refund', 'sale'),
            ('situation', 'general'),
        ],
        table='account_journal', write='sql')


def account_templates(env):
    # assign a chart template to configured companies in order not to
    # have the localization try to generate a new chart of accounts
    cr = env.cr
    account_templates = env['account.chart.template'].search([])
    configurable_template = env.ref('account.configurable_chart_template')
    account_templates -= configurable_template
    cr.execute('select distinct company_id from account_account where active')
    for company in env['res.company'].browse([i for i, in cr.fetchall()]):
        if company.chart_template_id:  # pragma: no cover
            # probably never happens, but we need to be sure not to overwrite
            # this anyways
            continue
        cr.execute(
            'select max(char_length(code)) from account_account '
            'where company_id=%s and parent_id is null', (company.id,))
        accounts_code_digits = cr.fetchall()[0][0]
        if len(account_templates) == 1:  # pragma: no cover
            # if there's only one template, we can be quite sure that's the
            # right one
            company.write({
                'chart_template_id': account_templates.id,
                'transfer_account_id': account_templates.transfer_account_id.id
            })
            # we need to write accounts_code_digits via sql because the orm
            # would try to renumber existing accounts which we don't want
            env.cr.execute(
                'update res_company set accounts_code_digits=%s '
                'where id in %s',
                (accounts_code_digits, tuple(company.ids)))
            continue
        # when there are multiple charts of accounts, things get messy.
        # we assign the chart of accounts with the most matches concerning
        # account codes (as names are more likely to change)
        best_template = configurable_template
        best_count = 0

        for template in account_templates:
            count = env['account.account'].search_count([
                ('code', 'in', template.account_ids.mapped('code')),
                ('company_id', '=', company.id),
            ])
            if count > best_count:
                best_count = count
                best_template = template
        openupgrade.message(
            cr, 'account', 'res_company', 'account_chart_template',
            'Fuzzily mapping company %d to chart template %d - this may be '
            'wrong', company, best_template)
        company.write({
            'chart_template_id': best_template.id,
            'transfer_account_id': best_template.transfer_account_id.id
        })
        # we need to write accounts_code_digits via sql because the orm would
        # try to renumber existing accounts which we don't want
        env.cr.execute(
            'update res_company set accounts_code_digits=%s where id in %s',
            (accounts_code_digits, tuple(company.ids)))


def parent_id_to_m2m(cr):
    cr.execute(
        'insert into account_tax_template_filiation_rel '
        '(parent_tax, child_tax) '
        'select id, parent_id from account_tax_template '
        'where parent_id is not null'
    )
    cr.execute(
        'insert into account_tax_filiation_rel '
        '(parent_tax, child_tax) '
        'select id, parent_id from account_tax where parent_id is not null'
    )


def parent_id_to_tag(env, model, tags_field='tag_ids', recursive=False):
    """Convert all parents of model to tags stored in tags_field.
    If recursive is true, create and assign tags for indirect parents too"""
    # TODO: This might be moved to openupgradelib
    cr = env.cr
    model = env[model]
    tags_model = env[model._fields[tags_field].comodel_name]
    parent2tag = {}
    cr.execute(
        'select id, %(parent_field)s from %(table)s where %(parent_field)s '
        'is not null' % {
            'parent_field': model._parent_name,
            'table': model._table,
        }
    )

    def handle_parent_for_child(child, parent):
        if parent.id not in parent2tag:
            parent2tag[parent.id] = tags_model.name_create(
                parent.display_name
            )[0]
        child.write(dict([
            (tags_field, [(4, parent2tag[parent.id])]),
        ]))
        if recursive:
            cr.execute(
                'select %(parent_field)s from account_account where id=%%s' % {
                    'parent_field': model._parent_name,
                },
                (parent.id,),
            )
            parent_ids = [p for p, in cr.fetchall() if p]
            if parent_ids:
                handle_parent_for_child(child, model.browse(parent_ids))

    for child_id, parent_id in cr.fetchall():
        handle_parent_for_child(
            model.browse(child_id), model.browse(parent_id)
        )


def cashbox(cr):
    # new cashbox lines are agnostic on whether they're opening or closing
    # lines
    cr.execute(
        'update account_cashbox_line set '
        'number=coalesce(%(number_closing)s, %(number_opening)s, 0)' % {
            'number_closing': openupgrade.get_legacy_name('number_closing'),
            'number_opening': openupgrade.get_legacy_name('number_opening'),
        }
    )
    # create a cashbox record per statement and old opening/closing state
    # first, create a temporary field to hold references
    cr.execute(
        'alter table account_bank_statement_cashbox '
        'add column %(cashbox_line_ids)s int[]' % {
            'cashbox_line_ids': openupgrade.get_legacy_name('cashbox_line_ids')
        }
    )
    cr.execute(
        'insert into account_bank_statement_cashbox '
        '(create_uid, create_date, write_uid, write_date, '
        '%(cashbox_line_ids)s) '
        'select s.create_uid, s.create_date, s.write_uid, s.write_date, '
        'array_agg(l.id) '
        'from account_cashbox_line l '
        'join account_bank_statement s '
        'on l.%(bank_statement_id)s=s.id '
        'group by s.id, l.%(number_closing)s is null, '
        'l.%(number_opening)s is null, '
        's.create_uid, s.create_date, s.write_uid, s.write_date' % {
            'number_closing': openupgrade.get_legacy_name('number_closing'),
            'number_opening': openupgrade.get_legacy_name('number_opening'),
            'bank_statement_id':
            openupgrade.get_legacy_name('bank_statement_id'),
            'cashbox_line_ids': openupgrade.get_legacy_name('cashbox_line_ids')
        }
    )
    # assign those to the cashbox lines they derive from
    cr.execute(
        'update account_cashbox_line l set cashbox_id='
        '(select id from account_bank_statement_cashbox where l.id='
        'any(%(cashbox_line_ids)s))' % {
            'cashbox_line_ids': openupgrade.get_legacy_name('cashbox_line_ids')
        }
    )
    # and now assign the proper cashbox_{start,end}_id values
    cr.execute(
        'update account_bank_statement s set '
        'cashbox_start_id=(select cashbox_id from account_cashbox_line where '
        '%(bank_statement_id)s=s.id and %(number_closing)s is null limit 1),'
        'cashbox_end_id=(select cashbox_id from account_cashbox_line where '
        '%(bank_statement_id)s=s.id and %(number_opening)s is null limit 1)' %
        {
            'number_closing': openupgrade.get_legacy_name('number_closing'),
            'number_opening': openupgrade.get_legacy_name('number_opening'),
            'bank_statement_id':
            openupgrade.get_legacy_name('bank_statement_id'),
        }
    )


def account_properties(cr):
    # Handle account properties as their names are changed.
    cr.execute("""
            update ir_property set name = 'property_account_payable_id',
            fields_id = (select id from ir_model_fields where model
            = 'res.partner' and name = 'property_account_payable_id')
            where name = 'property_account_payable' and (res_id like
            'res.partner%' or res_id is null)
            """)
    cr.execute("""
            update ir_property set fields_id = (select id from
            ir_model_fields where model = 'res.partner' and
            name = 'property_account_receivable_id'), name =
            'property_account_receivable_id' where
            name = 'property_account_receivable' and (res_id like
            'res.partner%' or res_id is null)
            """)


def account_internal_type(env):
    """type on accounts was replaced by internal_type which is a related field
    to the user type's type field"""
    cr = env.cr
    possible_types = map(
        operator.itemgetter(0),
        env['account.account.type']._fields['type'].selection,
    )
    for account_type in env['account.account.type'].search([]):
        cr.execute(
            'select %(type)s, array_agg(id) from account_account '
            'where user_type_id=%%s group by %(type)s '
            'order by %(type)s in %%s desc, '
            'array_length(array_agg(id), 1) desc' % {
                'type': openupgrade.get_legacy_name('type'),
            },
            (
                account_type.id,
                tuple(possible_types),
            )
        )
        type2ids = dict(cr.fetchall())
        if not type2ids:
            continue
        # type has default 'other', be sure that's a type actually used
        # in the existing accounts. The sorting above makes sure we pick
        # the type with most accounts
        if account_type.type not in type2ids:
            first_type = type2ids.keys()[0]
            account_type.write({
                'type': first_type if first_type in possible_types else 'other'
            })
        for legacy_type, ids in type2ids.iteritems():
            if legacy_type == account_type.type:
                continue
            default = {
                'type': legacy_type,
            }
            # for one of the deprecated types, use other but create a new
            # account type pointing to the deprecated type
            if legacy_type not in possible_types:
                default.update({
                    'name': '%s (%s)' % (
                        account_type.name,
                        legacy_type,
                    ),
                    'type': 'other',
                })
            env['account.account'].browse(ids).write({
                'user_type_id': account_type.copy(default=default).id,
            })


def map_account_tax_type(cr):
    """ See comments in method map_account_tax_type in the pre-migration
    script."""
    if not openupgrade.logged_query(cr, """
        select id FROM account_tax where {name_v8} = 'code'
    """.format(name_v8=openupgrade.get_legacy_name('type'))):
        return
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'amount_type',
        [('code', 'code')],
        table='account_tax', write='sql')


def map_account_tax_template_type(cr):
    """ See comments in method map_account_tax_type in the pre-migration
    script."""
    if not openupgrade.logged_query(cr, """
        select id FROM account_tax where {name_v8} = 'code'
    """.format(name_v8=openupgrade.get_legacy_name('type'))):
        return
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('type'), 'amount_type',
        [('code', 'code')],
        table='account_tax_template', write='sql')


def migrate_account_auto_fy_sequence(env):
    """As now Odoo implements a feature for having several sequence numbers
    per date range, we don't need anymore this module. This handles a smooth
    transition from v8 having it installed to v9 properly configured and
    without the module.
    """
    if not openupgrade.is_module_installed(env.cr, 'account_auto_fy_sequence'):
        return
    # Merge with the main module for avoid uninstallation of dependent modules
    openupgrade.update_module_names(
        env.cr, [('account_auto_fy_sequence', 'account')], merge_modules=True,
    )
    query = """
        UPDATE ir_sequence
        SET {0}=replace({0}, '%(fy)s', '%(range_year)s'),
            use_date_range=True
        WHERE {0} like '%\%(fy)s%'
        """
    env.cr.execute(query.format('prefix'))
    env.cr.execute(query.format('suffix'))


def fill_blacklisted_fields(cr):
    """Fill data of fields for which recomputation was surpressed."""
    # Set fields on account_move
    # matched_percentage will be set to 0.0, but be filled in migration
    #     of reconciliations.
    openupgrade.logged_query(
        cr,
        """\
        UPDATE account_move
         SET currency_id = subquery.currency_id,
             amount = subquery.amount,
             matched_percentage = 0.0
         FROM (SELECT
                am.id as id,
                rc.currency_id as currency_id,
               sum(aml.debit) as amount
            FROM account_move am
            JOIN res_company rc ON rc.id = am.company_id
            LEFT OUTER JOIN account_move_line aml ON aml.move_id = am.id
            GROUP BY am.id, rc.currency_id
        ) as subquery
        WHERE account_move.id = subquery.id
        """
    )
    # cash basis fields depend om matched_percentage, which will be filled
    # by reconciliation migration. For now will be filled with values that
    # are correct if associated journal is not for sale or purchase.
    openupgrade.logged_query(
        cr,
        """\
        UPDATE account_move_line
        SET amount_residual = 0.0,
            amount_residual_currency = 0.0,
            reconciled = False,
            company_currency_id = subquery.company_currency_id,
            balance = subquery.balance,
            debit_cash_basis = subquery.debit,
            credit_cash_basis = subquery.credit,
            balance_cash_basis = subquery.balance,
            user_type_id = subquery.user_type_id
        FROM (
            SELECT
                aml.id as id,
                rc.currency_id as company_currency_id,
                (aml.debit - aml.credit) as balance,
                aml.debit as debit,
                aml.credit as credit,
                aa.user_type_id as user_type_id
            FROM account_move_line aml
            JOIN res_company rc ON rc.id = aml.company_id
            JOIN account_account aa ON aa.id = aml.account_id
        ) as subquery
        WHERE account_move_line.id = subquery.id
        """
    )
    # Set fields on account_invoice_line
    # For the moment use practical rounding of result to 2 decimals,
    # no currency that I know of has more precision at the moment.
    openupgrade.logged_query(
        cr,
        """\
        WITH company_rate_selection AS (
            SELECT
                ai.id, com_cur.currency_id as company_currency_id,
                max(com_cur.name) as rate_date
            FROM account_invoice ai
            JOIN res_company com on ai.company_id = com.id
            LEFT OUTER JOIN res_currency_rate com_cur
                ON com.currency_id = com_cur.currency_id
                    AND ai.company_id =
                        COALESCE(com_cur.company_id, ai.company_id)
                    AND COALESCE(ai.date_invoice, date(ai.create_date)) >=
                        date(com_cur.name)
            GROUP BY ai.id, com_cur.currency_id
        )
        , invoice_rate_selection AS (
            SELECT
                ai.id, inv_cur.currency_id as invoice_currency_id,
                max(inv_cur.name) as rate_date
            FROM account_invoice ai
            JOIN res_company com on ai.company_id = com.id
            LEFT OUTER JOIN res_currency_rate inv_cur
                ON COALESCE(ai.currency_id, com.currency_id) =
                        inv_cur.currency_id
                    AND ai.company_id =
                        COALESCE(inv_cur.company_id, ai.company_id)
                    AND COALESCE(ai.date_invoice, date(ai.create_date)) >=
                        date(inv_cur.name)
            GROUP BY ai.id, inv_cur.currency_id
        )
        , effective_rates AS (
            SELECT
                ai.id as invoice_id,
                com_cur.rate as company_currency_rate,
                inv_cur.rate as invoice_currency_rate,
                (inv_cur.rate / com_cur.rate) as effective_rate
            FROM account_invoice ai
            JOIN company_rate_selection crs ON ai.id = crs.id
            JOIN res_currency_rate com_cur
                ON crs.company_currency_id = com_cur.currency_id
                    AND crs.rate_date = com_cur.name
            JOIN invoice_rate_selection irs ON ai.id = irs.id
            JOIN res_currency_rate inv_cur
                ON irs.invoice_currency_id = inv_cur.currency_id
                    AND irs.rate_date = inv_cur.name)
        , subquery(id, price_subtotal, price_subtotal_signed) AS (
            SELECT
                ail.id,
                ail.price_subtotal,
                CASE
                    WHEN ai.type IN ('in_refund', 'out_refund')
                    THEN ROUND(-ail.price_subtotal * er.effective_rate, 2)
                    ELSE ROUND(ail.price_subtotal  * er.effective_rate, 2)
                END
            FROM account_invoice_line ail
            JOIN account_invoice ai ON ail.invoice_id = ai.id
            JOIN effective_rates er ON ai.id = er.invoice_id
        )
        UPDATE account_invoice_line
        SET price_subtotal_signed = subquery.price_subtotal_signed
        FROM subquery
        WHERE account_invoice_line.id = subquery.id
        """
    )


def reset_blacklist_field_recomputation():
    """Make sure blacklists are disabled, to prevent problems in other
    modules.
    """
    from openerp.addons.account.models.account_move import \
        AccountMove, AccountMoveLine
    AccountMove._openupgrade_recompute_fields_blacklist = []
    AccountMoveLine._openupgrade_recompute_fields_blacklist = []
    from openerp.addons.account.models.account_invoice import \
        AccountInvoice, AccountInvoiceLine
    AccountInvoice._openupgrade_recompute_fields_blacklist = []
    AccountInvoiceLine._openupgrade_recompute_fields_blacklist = []


def fill_move_line_invoice(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_move_line aml
        SET invoice_id = ai.id
        FROM account_invoice ai,
            account_move am
        WHERE am.id = aml.move_id
            AND am.id = ai.move_id;
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    map_bank_state(cr)
    map_type_tax_use(cr)
    map_type_tax_use_template(cr)
    map_journal_state(cr)
    account_templates(env)
    parent_id_to_m2m(cr)
    cashbox(cr)
    account_properties(cr)
    # If the close_method is 'none', then set to 'False', otherwise set to
    # 'True'
    cr.execute("""
    UPDATE account_account_type SET include_initial_balance =  CASE
    WHEN %(openupgrade)s = 'none' THEN False
    ELSE True
    END
    """ % {'openupgrade': openupgrade.get_legacy_name('close_method')})

    # Set bank_statements_source to 'manual'
    cr.execute("""
    UPDATE account_journal SET bank_statements_source = 'manual'
    """)

    # Value 'percentage_of_total' => 'percentage'
    cr.execute("""
    UPDATE account_operation_template SET amount_type = 'percentage'
    WHERE amount_type = 'percentage_of_total'
    """)

    # Set up anglosaxon accounting
    cr.execute(
        "UPDATE res_company SET anglo_saxon_accounting = %s",
        (openupgrade.is_module_installed(cr, 'account_anglo_saxon'), ),
    )

    # deprecate accounts where active is False
    cr.execute("""
    UPDATE account_account SET deprecated = True WHERE active = False
    """)

    # Set display_on_footer to False
    cr.execute("""
    UPDATE account_journal SET display_on_footer = False
    """)

    # Logic to move from child_ids to children_tax_ids (o2m => m2m)
    cr.execute("""
    INSERT INTO account_tax_filiation_rel (parent_tax, child_tax)
    SELECT parent_id, id from account_tax WHERE parent_id IS NOT NULL
    """)

    # Get parent_id and insert it into children_tax_ids (m2o => m2m)
    cr.execute("""
    INSERT INTO account_tax_template_filiation_rel (parent_tax, child_tax)
    SELECT parent_id, id from account_tax_template WHERE parent_id IS NOT NULL
    """)

    # In v8, if child_depend == True, then in v9, set amount_type='group'
    cr.execute("""
    UPDATE account_tax SET amount_type = 'group'
    WHERE child_depend IS True
    """)
    cr.execute("""
    UPDATE account_tax_template SET amount_type = 'group'
    WHERE child_depend IS True
    """)

    # In v9, percentages are expressed as hundred-based percentage,
    # not one-based percentage
    cr.execute('UPDATE account_tax set amount=amount*100 '
               "WHERE amount_type='percent'")

    registry = RegistryManager.get(cr.dbname)
    openupgrade.m2o_to_x2m(
        cr, registry['account.bank.statement.line'],
        'account_bank_statement_line',
        'journal_entry_ids',
        openupgrade.get_legacy_name('journal_entry_id'),
    )

    parent_id_to_tag(env, 'account.tax')
    parent_id_to_tag(env, 'account.account', recursive=True)
    account_internal_type(env)
    map_account_tax_type(cr)
    map_account_tax_template_type(cr)
    migrate_account_auto_fy_sequence(env)
    fill_blacklisted_fields(cr)
    reset_blacklist_field_recomputation()
    fill_move_line_invoice(cr)
