# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import operator
from openerp import models
from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager
from openerp.tools import float_compare


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


def _get_pair_to_reconcile(moves, amount_residual):

    # field is either 'amount_residual' or 'amount_residual_currency'
    # (if the reconciled account has a secondary currency set)
    field = moves[0].account_id.currency_id \
            and 'amount_residual_currency' or 'amount_residual'
    rounding = moves[0].company_id.currency_id.rounding
    if moves[0].currency_id \
            and all([x.amount_currency and
                    x.currency_id == moves[0].currency_id
                     for x in moves]):
        # or if all lines share the same currency
        field = 'amount_residual_currency'
        rounding = moves[0].currency_id.rounding
    # target the pair of move in self that are the oldest
    sorted_moves = sorted(moves, key=lambda a: a.date)
    debit = credit = False
    for aml in sorted_moves:
        if credit and debit:
            break
        if float_compare(amount_residual[aml.id][field], 0,
                         precision_rounding=rounding) == 1 \
                and not debit:
            debit = aml
        elif float_compare(amount_residual[aml.id][field], 0,
                           precision_rounding=rounding) == -1 \
                and not credit:
            credit = aml
    return debit, credit


def auto_reconcile_lines(env, move_lines, amount_residual):

    if not move_lines:
        return move_lines

    sm_debit_move, sm_credit_move = _get_pair_to_reconcile(move_lines,
                                                           amount_residual)
    # there is no more pair to reconcile so return what move_line are left
    if not sm_credit_move or not sm_debit_move:
        return move_lines

    field = move_lines[0].account_id.currency_id \
        and 'amount_residual_currency' or 'amount_residual'
    if not sm_debit_move.debit and not sm_debit_move.credit:
        # both debit and credit field are 0, consider
        # the amount_residual_currency field because it's an
        # exchange difference entry
        field = 'amount_residual_currency'
    if move_lines[0].currency_id and all(
            [x.currency_id == move_lines[0].currency_id for x in move_lines]):
        # all the lines have the same currency, so we consider
        # the amount_residual_currency field
        field = 'amount_residual_currency'
    # Reconcile the pair together
    amount_reconcile = \
        min(amount_residual[sm_debit_move.id][field],
            -amount_residual[sm_credit_move.id][field])
    # Remove from recordset the one(s) that will be totally reconciled
    if amount_reconcile == amount_residual[sm_debit_move.id][field]:
        move_lines -= sm_debit_move
    if amount_reconcile == -amount_residual[sm_credit_move.id][field]:
        move_lines -= sm_credit_move

    # Check for the currency and amount_currency we can set
    currency = False
    amount_reconcile_currency = 0
    if sm_debit_move.currency_id == sm_credit_move.currency_id and \
            sm_debit_move.currency_id.id:
        currency = sm_credit_move.currency_id.id
        amount_reconcile_currency = min(
            amount_residual[sm_debit_move.id]['amount_residual_currency'],
            -amount_residual[sm_credit_move.id]['amount_residual_currency'])
        amount_residual[sm_debit_move.id][
            'amount_residual_currency'] -= amount_reconcile
        amount_residual[sm_credit_move.id][
            'amount_residual_currency'] -= amount_reconcile

    amount_reconcile = min(amount_residual[sm_debit_move.id][
                               'amount_residual'],
                           -amount_residual[sm_credit_move.id][
                               'amount_residual'])
    amount_residual[sm_debit_move.id]['amount_residual'] -= amount_reconcile
    amount_residual[sm_credit_move.id]['amount_residual'] -= amount_reconcile

    openupgrade.logged_query(env.cr, """
        INSERT INTO account_partial_reconcile
        (debit_move_id, credit_move_id, amount, amount_currency,
        currency_id)
        VALUES (%s, %s, %s, %s, %s)
    """ % (sm_debit_move.id, sm_credit_move.id, amount_reconcile,
           amount_reconcile_currency, currency))

    # Iterate process again on self
    return auto_reconcile_lines(env, move_lines, amount_residual)


def account_partial_reconcile(env):
    """ Create new entries of model account.partial.reconcile that replace the
    obsolete account.move.reconcile model. Note that an additional model
    'account.full.reconcile' was introduced after the release of 9.0 in its own
    automatically installed module.

    Disable all workflow steps that are meant to run on new reconciliations
    """
    set_workflow_org = models.BaseModel.step_workflow
    models.BaseModel.step_workflow = lambda *args, **kwargs: None
    cr = env.cr

    # Execute a direct reconciliation for the most common and easiest use
    # case, that involves reconciling two moves, for the full amount, and in
    # the company currency. This will dramatically improve the overall
    # performance of the migration of reconciliations.
    openupgrade.logged_query(cr, """
        WITH Q1 AS (
            SELECT reconcile_id, sum(debit-credit) as balance,
            count(id) as num_moves, count(currency_id) as num_currencies
            FROM account_move_line
            WHERE reconcile_id IS NOT NULL
            GROUP BY reconcile_id, currency_id
        ),
        Q2 AS (
            SELECT reconcile_id
            FROM Q1
            WHERE balance = 0.0
            AND num_moves = 2
            AND num_currencies = 0
        ),
        Q3 AS (
            SELECT aml.reconcile_id, aml.id, aml.debit,
            aml.credit, aml.company_id
            FROM account_move_line AS aml
            INNER JOIN Q2
            ON Q2.reconcile_id = aml.reconcile_id
        ),
        Q4 AS (
            SELECT reconcile_id,
            CASE WHEN debit > 0.0
            THEN id ELSE Null END as debit_move_id, CASE WHEN credit > 0.0
            THEN id ELSE Null END as credit_move_id,
            CASE WHEN debit > 0.0 THEN debit END as amount, company_id
            FROM Q3
            GROUP BY reconcile_id, debit_move_id, credit_move_id, amount,
            company_id
        ),
        Q5 AS (
            SELECT reconcile_id, sum(debit_move_id) as debit_move_id,
            sum(credit_move_id) as credit_move_id, sum(amount) as amount,
            company_id
            FROM Q4
            GROUP BY reconcile_id, company_id
        )
        INSERT INTO account_partial_reconcile
        (create_uid, create_date, write_uid, write_date, debit_move_id,
        credit_move_id, amount, company_id, amount_currency)
        SELECT amr.create_uid, amr.create_date, amr.write_uid,
        amr.write_date, Q5.debit_move_id, Q5.credit_move_id, Q5.amount,
        Q5.company_id, 0.0
        FROM Q5
        INNER JOIN account_move_reconcile AS amr
        ON Q5.reconcile_id = amr.id
        WHERE debit_move_id > 0 AND credit_move_id > 0
    """)

    # We want to exclude the moves that were included in the step above from
    # the next reconciliation step.
    cr.execute("""
        WITH Q1 AS (
            SELECT reconcile_id, sum(debit-credit) as balance,
            count(id) as num_moves, count(currency_id) as num_currencies
            FROM account_move_line
            WHERE reconcile_id IS NOT NULL
            GROUP BY reconcile_id, currency_id
        ),
        Q2 AS (
            SELECT reconcile_id
            FROM Q1
            WHERE balance = 0.0
            AND num_moves = 2
            AND num_currencies = 0
        )
        SELECT aml.id
        FROM account_move_line AS aml
        INNER JOIN Q2
        ON Q2.reconcile_id = aml.reconcile_id
    """)

    move_line_ids_reconciled = [move_line_id for move_line_id,
                                in cr.fetchall()]

    # The previous move lines must be flagged as reconciled. The residual
    # amount is 0.
    move_lines = env['account.move.line'].with_context(recompute=False).browse(
        move_line_ids_reconciled)
    for move_line in move_lines:
        move_line.reconciled = True
        move_line.amount_residual = 0.0
        move_line.amount_residual_currency = 0.0

    move_line_map = {}
    cr.execute("SELECT reconcile_id, id "
               "FROM account_move_line "
               "WHERE reconcile_id IS NOT NULL "
               "AND id NOT IN %s" % (tuple(move_line_ids_reconciled), ))
    rec_l = {}
    for rec_id, move_line_id in cr.fetchall():
        move_line_map.setdefault(rec_id, []).append(move_line_id)
        rec_l[rec_id] = True
    num_recs = len(rec_l.keys())
    i = 1
    for _rec_id, move_line_ids in move_line_map.iteritems():
        msg = 'Reconciliation step 2 (%s of %s). ' \
              'Resolving account.move.reconcile %s.' % \
              (i, num_recs, _rec_id)
        openupgrade.message(cr, 'account', 'account_partial_reconcile',
                            'id', msg)
        move_lines = env['account.move.line'].browse(move_line_ids)
        amount_residual_d = {}
        for move_line in move_lines:
            amount = abs(move_line.debit - move_line.credit)
            amount_residual_currency = abs(move_line.amount_currency) or 0.0
            sign = 1 if (move_line.debit - move_line.credit) > 0 else -1
            amount_residual = move_line.company_id.currency_id.round(
                amount * sign)
            amount_residual_d[move_line.id] = {}
            amount_residual_d[move_line.id]['amount_residual'] = \
                amount_residual
            amount_residual_d[move_line.id]['amount_residual_currency'] = \
                move_line.currency_id and move_line.currency_id.round(
                    amount_residual_currency * sign) or 0.0
        auto_reconcile_lines(env, move_lines, amount_residual_d)
        i += 1
        move_line_ids_reconciled += move_line_ids

    # Update the table that relates invoices with payments made
    openupgrade.logged_query(cr, """
        INSERT INTO account_invoice_account_move_line_rel
        (account_invoice_id, account_move_line_id)
        SELECT DISTINCT ai.id, apr.debit_move_id
        FROM account_partial_reconcile AS apr
        INNER JOIN account_move_line as aml
        ON aml.id = apr.credit_move_id
        INNER JOIN account_invoice as ai
        ON ai.move_id = aml.move_id
        WHERE apr.credit_move_id IN %s
    """ % (tuple(move_line_ids_reconciled),))

    openupgrade.logged_query(cr, """
        INSERT INTO account_invoice_account_move_line_rel
        (account_invoice_id, account_move_line_id)
        SELECT DISTINCT ai.id, apr.credit_move_id
        FROM account_partial_reconcile AS apr
        INNER JOIN account_move_line as aml
        ON aml.id = apr.debit_move_id
        INNER JOIN account_invoice as ai
        ON ai.move_id = aml.move_id
        WHERE apr.debit_move_id IN %s
    """ % (tuple(move_line_ids_reconciled), ))

    # Migrate partially reconciled items
    move_line_map = {}
    cr.execute("SELECT COALESCE(reconcile_id, reconcile_partial_id), id "
               "FROM account_move_line "
               "WHERE (reconcile_id IS NOT NULL "
               "OR reconcile_partial_id IS NOT NULL) "
               "AND id NOT IN %s" % (tuple(move_line_ids_reconciled), ))
    rec_l = {}
    for rec_id, move_line_id in cr.fetchall():
        move_line_map.setdefault(rec_id, []).append(move_line_id)
        rec_l[rec_id] = True
    num_recs = len(rec_l.keys())
    to_recompute = env['account.move.line']
    i = 1
    for _rec_id, move_line_ids in move_line_map.iteritems():
        msg = 'Reconciliation step 3 (%s of %s). ' \
              'Resolving account.move.reconcile %s.' % (i, num_recs, _rec_id)
        openupgrade.message(cr, 'account', 'account_partial_reconcile',
                            'id', msg)
        move_lines = env['account.move.line'].browse(move_line_ids)
        move_lines.auto_reconcile_lines()
        i += 1
        to_recompute += move_lines
    for field in ['amount_residual', 'amount_residual_currency', 'reconciled']:
        env.add_todo(env['account.move.line']._fields[field], to_recompute)
    env['account.move.line'].recompute()
    models.BaseModel.step_workflow = set_workflow_org


def invoice_recompute(env):
    set_workflow_org = models.BaseModel.step_workflow
    models.BaseModel.step_workflow = lambda *args, **kwargs: None
    to_recompute = env['account.invoice'].search([])
    for field in ['residual', 'residual_signed', 'residual_company_signed']:
        env.add_todo(env['account.invoice']._fields[field], to_recompute)
    env['account.invoice'].recompute()
    models.BaseModel.step_workflow = set_workflow_org


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
    account_partial_reconcile(env)
    invoice_recompute(env)
    map_account_tax_type(cr)
    map_account_tax_template_type(cr)
