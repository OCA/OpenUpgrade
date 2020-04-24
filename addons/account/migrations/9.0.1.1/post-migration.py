# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import operator
from openupgradelib import openupgrade, openupgrade_90
from openerp.modules.registry import RegistryManager
from psycopg2.extensions import AsIs

_logger = logging.getLogger('account.migrations.9.0.1.1.post_migration')


account_type_map = [
    ('account.data_account_type_cash', 'account.data_account_type_liquidity'),
    ('account.conf_account_type_chk', 'account.data_account_type_liquidity'),
    ('account.conf_account_type_tax',
     'account.data_account_type_current_liabilities'),
]


def recompute_multicurrency_invoices(env):
    """ Overwrite the simple non multicurrency SQL computations
    by triggering the compute method for multicurrency invoices. """
    env.cr.execute(
        """ SELECT ai.id
        FROM account_invoice ai
        JOIN res_company rc ON ai.company_id = rc.id
        WHERE ai.currency_id != rc.currency_id """)
    invoice_ids = [invoice_id for invoice_id, in env.cr.fetchall()]
    _logger.info(
        'Triggering recompute of amount fields for %s multicurrency '
        'invoices', len(invoice_ids))
    model = env['account.invoice']
    env.add_todo(model._fields['amount_tax'], model.browse(invoice_ids))
    model.recompute()


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
        'update account_cashbox_line l set cashbox_id=cb.id '
        'from (select id, openupgrade_legacy_9_0_cashbox_line_ids from '
        'account_bank_statement_cashbox) cb '
        'where l.id=any(%(cashbox_line_ids)s)' % {
            'cashbox_line_ids': openupgrade.get_legacy_name('cashbox_line_ids')
        }
    )
    # and now assign the proper cashbox_start_id values
    cr.execute(
        'update account_bank_statement s '
        'set cashbox_start_id=cbl.cashbox_id '
        'from (select cashbox_id, %(bank_statement_id)s,  '
        '%(number_closing)s from account_cashbox_line) cbl '
        'where s.id=cbl.%(bank_statement_id)s and %(number_closing)s is null' %
        {
            'number_closing': openupgrade.get_legacy_name('number_closing'),
            'bank_statement_id':
            openupgrade.get_legacy_name('bank_statement_id'),
        }
    )

    # and now assign the proper cashbox_end_id values
    cr.execute(
        'update account_bank_statement s set cashbox_end_id=cbl.cashbox_id '
        'from (select cashbox_id, %(bank_statement_id)s, %(number_opening)s '
        ' from account_cashbox_line) cbl '
        'where s.id=cbl.%(bank_statement_id)s and %(number_opening)s is null' %
        {
            'number_opening': openupgrade.get_legacy_name('number_opening'),
            'bank_statement_id':
            openupgrade.get_legacy_name('bank_statement_id'),
        }
    )


def account_properties(cr):
    # Handle account properties as their names are changed.
    cr.execute("""
        update ir_property set name = 'property_account_payable_id',
            fields_id = f.id
        from (select id from ir_model_fields where model
            = 'res.partner' and name = 'property_account_payable_id') f
            where name = 'property_account_payable' and (res_id like
            'res.partner%' or res_id is null)
           """)
    cr.execute("""
            update ir_property set name = 'property_account_receivable_id',
            fields_id = f.id
            from (select id from
            ir_model_fields where model = 'res.partner' and
            name = 'property_account_receivable_id') f  where
            name = 'property_account_receivable' and (res_id like
            'res.partner%' or res_id is null)
            """)


def move_view_accounts(env):
    """Move accounts of type view to another table, but removing them from the
    main list for not disturbing normal accounting.
    """
    openupgrade.logged_query(
        env.cr, """
        CREATE TABLE %s
        AS SELECT * FROM account_account
        WHERE %s = 'view'""", (
            AsIs(openupgrade.get_legacy_name('account_account')),
            AsIs(openupgrade.get_legacy_name('type')),
        )
    )
    # Truncate this transient model table that refers to view accounts
    openupgrade.logged_query(
        env.cr,
        """TRUNCATE account_vat_declaration,
            account_journal_account_vat_declaration_rel""")
    # Remove constraint that delete in cascade children accounts
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_account
        DROP CONSTRAINT account_account_parent_id_fkey"""
    )
    openupgrade.logged_query(
        env.cr, """
        DELETE FROM account_account
        WHERE %s = 'view'""", (AsIs(openupgrade.get_legacy_name('type')),)
    )
    # Remove constraint also on templates
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_account_template
        DROP CONSTRAINT account_account_template_parent_id_fkey"""
    )


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


def migrate_account_sequence_fiscalyear(cr):
    """ Migrate subsequences from fiscalyears to sequence date ranges
    so that the next number is aligned with the last assigned number """
    openupgrade.logged_query(
        cr,
        """ \
        INSERT into ir_sequence_date_range
        (sequence_id, date_from, date_to, number_next)
        SELECT sequence_main_id, af.date_start, af.date_stop,
            irs.number_next
        FROM account_sequence_fiscalyear asf,
            account_fiscalyear af, ir_sequence irs
        WHERE asf.fiscalyear_id = af.id
             and asf.sequence_id = irs.id; """)
    openupgrade.logged_query(
        cr,
        """ \
        UPDATE ir_sequence SET
            prefix = REPLACE(prefix, '%%(year)s', '%%(range_year)s'),
            suffix = REPLACE(suffix, '%%(year)s', '%%(range_year)s'),
            use_date_range = TRUE
        WHERE id IN (SELECT sequence_id FROM ir_sequence_date_range)
        """)


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


def _fill_aml_tax_line_ids(env, amls, tax_id, tax_amounts):
    move_line_obj = env['account.move.line']
    lines_to_write = env['account.move.line'].with_context(
        check_move_validity=False)
    for line in openupgrade.chunked(amls):
        if not line.debit and not line.credit:
            # Extra line generated by previous <v8 constraint
            # of one tax code per line. We need to find the
            # line for the same amount to put the base there
            env.cr.execute(
                """
                SELECT id
                FROM account_move_line
                WHERE (
                    debit = %(amount)s OR
                    credit = %(amount)s
                ) AND move_id = %(move_id)s
                """, {
                    'amount': tax_amounts[line.id],
                    'move_id': line.move_id.id,
                }
            )
            row_base2 = env.cr.fetchone()
            while row_base2:
                # for multiple lines with same amount
                line = move_line_obj.browse(row_base2[0])
                if tax_id not in line.tax_ids.ids:
                    lines_to_write |= line
                    break
                row_base2 = env.cr.fetchone()
        else:
            lines_to_write |= line
    lines_to_write.write({'tax_ids': [(4, tax_id)]})


def fill_move_taxes(env):
    """Try to deduce taxes in account move lines from old tax codes.

    Method followed:

    Tax amounts
    -----------

    * If the tax code is present in only one tax as tax code, then we can fill
      tax_line_id with that tax.
    * If there are more than one tax with that tax code, try to match tax lines
      with the name of the move line.

    Base amounts
    ------------

    * If the tax code is present in only one tax as base code, then we can add
      that tax to tax_ids.
    * If there are more than one for base amounts, see tax codes for other
      lines in the same move and try to match entire tax. If matched exactly
      with one tax, we can have 2 cases:

       * The move line has debit/credit: then we just put the tax as base.
       * It's a dummy line introduced for adding another base tax code, due to
         the restriction of <v8 of only one tax code per line. We locate the
         first line in the same move with the same amount in debit or credit
         column that doesn't have this tax already as base tax.

    * If still no success, then we make a last try searching only for active
      taxes to see if this way we match only one record.
    """
    env.cr.execute(
        "SELECT tax_code_id FROM account_move_line GROUP BY tax_code_id"
    )
    deferred_base_tax_code_ids = []
    for row in env.cr.fetchall():
        tax_code_id = row[0]
        # TAX AMOUNT
        env.cr.execute(
            """SELECT COUNT(*), MAX(id) FROM account_tax
            WHERE tax_code_id=%(tax_code_id)s
            OR ref_tax_code_id=%(tax_code_id)s""",
            {'tax_code_id': tax_code_id},
        )
        row_tax = env.cr.fetchone()
        if row_tax[0] == 1:
            openupgrade.logged_query(
                env.cr,
                """UPDATE account_move_line
                SET tax_line_id = %s
                WHERE tax_code_id = %s""", (row_tax[1], tax_code_id)
            )
        elif row_tax[0] > 1:
            # Try to match by tax name (put on the description of the line)
            env.cr.execute(
                """SELECT name
                FROM account_move_line
                WHERE tax_code_id = %s
                GROUP BY name""", (tax_code_id, )
            )
            for row_name in env.cr.fetchall():
                # Look for a match also on translated terms
                env.cr.execute(
                    """SELECT COUNT(DISTINCT(t.id)), MAX(t.id)
                    FROM account_tax t
                    LEFT JOIN ir_translation tr
                    ON tr.name='account.tax,name' AND tr.res_id = t.id
                    WHERE (
                        t.tax_code_id = %(tax_code_id)s OR
                        t.ref_tax_code_id = %(tax_code_id)s
                    )
                    AND (
                        t.name = %(name)s OR
                        tr.value = %(name)s
                    )""", {
                        'tax_code_id': tax_code_id,
                        'name': row_name[0],
                    },
                )
                row_tax = env.cr.fetchone()
                if row_tax[0] == 1:
                    openupgrade.logged_query(
                        env.cr,
                        """UPDATE account_move_line
                        SET tax_line_id = %s
                        WHERE tax_code_id = %s
                        AND name = %s
                        """, (row_tax[1], tax_code_id, row_name[0])
                    )
        # BASE AMOUNT
        env.cr.execute(
            """SELECT COUNT(*), MAX(id) FROM account_tax
            WHERE base_code_id=%(tax_code_id)s OR
            ref_base_code_id=%(tax_code_id)s
            """, {'tax_code_id': tax_code_id},
        )
        row_base = env.cr.fetchone()
        if row_base[0] == 1:
            env.cr.execute(
                """SELECT id, tax_amount
                FROM account_move_line
                WHERE tax_code_id=%s""", (tax_code_id,),
            )
            line_rows = env.cr.fetchall()
            tax_amounts = dict(line_rows)
            amls = env['account.move.line'].with_context(
                check_move_validity=False).browse(tax_amounts.keys())
            _fill_aml_tax_line_ids(env, amls, row_base[1], tax_amounts)
        elif row_base[0] > 1:
            # Let complete all the tax fee codes before doing the rest of the
            # heuristics, as it depends on them
            deferred_base_tax_code_ids.append(tax_code_id)
    for tax_code_id in deferred_base_tax_code_ids:
        env.cr.execute(
            """SELECT id, tax_amount
            FROM account_move_line
            WHERE tax_code_id=%s""", (tax_code_id, ),
        )
        line_rows = env.cr.fetchall()
        tax_amounts = dict(line_rows)
        amls = env['account.move.line'].browse(tax_amounts.keys())
        # Match base tax using the already assigned tax fees
        matched = False
        for line in amls:
            env.cr.execute(
                """SELECT tax_line_id
                FROM account_move_line
                WHERE move_id = %s""", (line.move_id.id, ),
            )
            fee_tax_ids = [x[0] for x in env.cr.fetchall() if x[0]]
            if fee_tax_ids:
                env.cr.execute(
                    """SELECT COUNT(*), MAX(id) FROM account_tax
                    WHERE (
                       base_code_id=%(tax_code_id)s OR
                       ref_base_code_id=%(tax_code_id)s
                    ) AND id IN %(tax_ids)s
                    """, {
                        'tax_code_id': tax_code_id,
                        'tax_ids': tuple(fee_tax_ids),
                    },
                )
                row_base = env.cr.fetchone()
                if row_base[0] == 1:
                    matched = True
                    _fill_aml_tax_line_ids(env, line, row_base[1], tax_amounts)
        if not matched:
            # Try with only active taxes
            env.cr.execute(
                """SELECT COUNT(*), MAX(id) FROM account_tax
                WHERE (
                    base_code_id=%(tax_code_id)s OR
                    ref_base_code_id=%(tax_code_id)s
                ) AND active=True
                """, {'tax_code_id': tax_code_id},
            )
            row_base = env.cr.fetchone()
            if row_base[0] == 1:
                _fill_aml_tax_line_ids(env, amls, row_base[1], tax_amounts)


def fill_account_invoice_tax_taxes(env, manual_tax_code_mapping=None):
    """Fill tax_id field from old base_code_id and tax_code_id fields from v8.

    This method can be called several times from other migration scripts, as it
    doesn't overwrite lines already filled, and it's intended to be used by
    other migration scripts, mostly localization modules (l10n_*) that needs
    to adjust mapping, for example if there has been several tax changes across
    time. There's a parameter for that purpose.

    :param: manual_tax_code_mapping: List of tuples for indicating mappings
      from old tax codes (first element of the tuple) to newest ones (second
      element).
    """
    if manual_tax_code_mapping is None:
        manual_tax_code_mapping = []
    env.cr.execute(
        """SELECT base_code_id, tax_code_id
        FROM account_invoice_tax
        WHERE tax_id IS NULL
        GROUP BY base_code_id, tax_code_id"""
    )
    for row in env.cr.fetchall():
        base_code_id = row[0]
        tax_code_id = row[1]
        _fill_account_invoice_tax_taxes_recursive(
            env, base_code_id, tax_code_id,
            manual_tax_code_mapping=manual_tax_code_mapping,
        )


def _fill_account_invoice_tax_taxes_recursive(env, base_code_id, tax_code_id,
                                              original_base_code_id=0,
                                              original_tax_code_id=0,
                                              bypass_exact_match=False,
                                              manual_tax_code_mapping=None):
    """This makes the dirty work of filling taxes or calling itself with
    other parameters.

    Method followed
    ===============

    * If both codes are present in only one tax, then we can safely fill
      tax_id with that tax.
    * If there are more than one tax with that tax codes, try to match tax
      with the name of the tax line.
    * If still no single match, try to match only with active taxes.
    * Finally, if there is no match, see if there's any tax code manual mapping
      for starting again the matching.
    """
    if not original_base_code_id:
        original_base_code_id = base_code_id
    if not original_tax_code_id:
        original_tax_code_id = tax_code_id
    # Using `IS NOT DISTINCT FROM` for avoiding problems with NULL values
    env.cr.execute(
        """SELECT COUNT(*), MAX(id) FROM account_tax
        WHERE (
            base_code_id IS NOT DISTINCT FROM %(base_code_id)s AND
            tax_code_id IS NOT DISTINCT FROM %(tax_code_id)s
        ) OR (
            ref_base_code_id IS NOT DISTINCT FROM %(base_code_id)s AND
            ref_tax_code_id IS NOT DISTINCT FROM %(tax_code_id)s
        )""", {
            'base_code_id': base_code_id or AsIs('NULL'),
            'tax_code_id': tax_code_id or AsIs('NULL'),
        },
    )
    row_tax = env.cr.fetchone()
    if row_tax[0] == 1 and not bypass_exact_match:
        # EXACT MATCH
        openupgrade.logged_query(
            env.cr,
            """UPDATE account_invoice_tax
            SET tax_id = %s
            WHERE base_code_id IS NOT DISTINCT FROM %s
            AND tax_code_id IS NOT DISTINCT FROM %s
            AND tax_id IS NULL""", (
                row_tax[1],
                original_base_code_id or AsIs('NULL'),
                original_tax_code_id or AsIs('NULL'),
            )
        )
    elif row_tax[0] > 1 or bypass_exact_match:
        # MULTIPLE MATCHES - SEARCH BY NAME
        env.cr.execute(
            """SELECT name, company_id
            FROM account_invoice_tax
            WHERE base_code_id = %s AND tax_code_id = %s AND tax_id IS NULL
            GROUP BY name, company_id
            """, (
                original_base_code_id,
                original_tax_code_id,
            )
        )
        for row_name in env.cr.fetchall():
            # Make 2 passes - The second one only considering active taxes
            for i in range(2):
                # Look for a match also on translated terms
                query = """
                    SELECT COUNT(DISTINCT(t.id)), MAX(t.id)
                    FROM account_tax t
                    LEFT JOIN ir_translation tr
                    ON tr.name='account.tax,name' AND tr.res_id = t.id
                    WHERE ((
                        base_code_id IS NOT DISTINCT FROM %(base_code_id)s AND
                        tax_code_id IS NOT DISTINCT FROM %(tax_code_id)s
                    ) OR (
                        ref_base_code_id IS NOT DISTINCT FROM %(base_code_id)s
                        AND
                        ref_tax_code_id IS NOT DISTINCT FROM %(tax_code_id)s
                    ))
                    AND t.company_id = %(company_id)s
                    AND (
                        t.name = %(name)s OR
                        tr.value = %(name)s
                    )"""
                if i == 1:
                    query += " AND t.active"
                env.cr.execute(
                    query, {
                        'base_code_id': base_code_id or AsIs('NULL'),
                        'tax_code_id': tax_code_id or AsIs('NULL'),
                        'name': row_name[0],
                        'company_id': row_name[1],
                    },
                )
                row_tax = env.cr.fetchone()
                if row_tax[0] == 1:
                    openupgrade.logged_query(
                        env.cr,
                        """UPDATE account_invoice_tax
                        SET tax_id = %s
                        WHERE base_code_id IS NOT DISTINCT FROM %s
                        AND tax_code_id IS NOT DISTINCT FROM %s
                        AND name = %s
                        AND company_id = %s
                        AND tax_id IS NULL
                        """, (
                            row_tax[1],
                            original_base_code_id or AsIs('NULL'),
                            original_tax_code_id or AsIs('NULL'),
                            row_name[0],
                            row_name[1],
                        )
                    )
                    break
    else:
        # NO MATCH - TRY TO MAKE REPLACEMENT
        query_name = "SELECT name FROM account_tax_group WHERE id = %s"
        query_id = "SELECT id FROM account_tax_group WHERE name = %s"
        env.cr.execute(query_name, (base_code_id,))
        base_row = env.cr.fetchone()
        env.cr.execute(query_name, (tax_code_id,))
        tax_row = env.cr.fetchone()
        if not base_row or not tax_row:
            return
        base_code_name = base_row[0]
        tax_code_name = tax_row[0]
        # This allows to search also when only tax code name is mapped, but
        # base code name is not mapped
        mappings = [(False, False)] + manual_tax_code_mapping
        for old_base_name, new_base_name in mappings:
            # Look for mapping for base codes
            if old_base_name and old_base_name != base_code_name:
                continue
            if old_base_name:
                env.cr.execute(query_id, (new_base_name, ))
                row_base = env.cr.fetchone()
                if not row_base:
                    continue
            else:
                row_base = [base_code_id]
            second_match = False
            for old_tax_name, new_tax_name in manual_tax_code_mapping:
                if old_tax_name != tax_code_name:
                    continue
                second_match = True
                env.cr.execute(query_id, (new_tax_name, ))
                row_tax = env.cr.fetchone()
                if not row_tax:
                    continue
                _fill_account_invoice_tax_taxes_recursive(
                    env, row_base[0], row_tax[0],
                    original_base_code_id=base_code_id,
                    original_tax_code_id=tax_code_id,
                    bypass_exact_match=True,
                    manual_tax_code_mapping=manual_tax_code_mapping,
                )
            if not second_match and new_base_name:
                _fill_account_invoice_tax_taxes_recursive(
                    env, row_base[0], tax_code_id,
                    original_base_code_id=base_code_id,
                    original_tax_code_id=tax_code_id,
                    bypass_exact_match=True,
                    manual_tax_code_mapping=manual_tax_code_mapping,
                )


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
                (CASE
                    WHEN ai.type IN ('in_refund', 'out_refund')
                    THEN ROUND(-ail.price_subtotal / er.effective_rate, 2)
                    ELSE ROUND(ail.price_subtotal  / er.effective_rate, 2)
                END) AS price_subtotal_signed,
                ai.currency_id AS currency_id
            FROM account_invoice_line ail
            JOIN account_invoice ai ON ail.invoice_id = ai.id
            JOIN effective_rates er ON ai.id = er.invoice_id
        )
        UPDATE account_invoice_line
        SET price_subtotal_signed = subquery.price_subtotal_signed,
            currency_id = subquery.currency_id
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


@openupgrade.logging()
def fast_compute_cash_basis(env):
    """Recompute faster these fields"""
    # Replace https://github.com/OCA/OpenUpgrade/blob/7a49881f87c0aa6ef29c/addons/account/models/account_move.py#L44-L62
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move
            SET matched_percentage = sub.matched_percentage
            FROM (
                SELECT
                    aml.move_id,
                    CASE
                        WHEN 0.0 = ROUND(
                            SUM(ABS(COALESCE(aml.debit, 0.0) - COALESCE(aml.credit, 0.0))),
                            CASE
                                WHEN MAX(rc.rounding) < 1
                                THEN CEIL(LOG(1 / MAX(rc.rounding)))
                                ELSE 0
                            END::INTEGER
                        )
                        THEN 1.0
                        ELSE SUM(COALESCE(apr.amount, 0)) / SUM(ABS(COALESCE(aml.debit, 0) - COALESCE(aml.credit, 0)))
                    END AS matched_percentage
                FROM
                    account_move_line aml
                    LEFT JOIN account_partial_reconcile apr
                    ON aml.id = apr.credit_move_id OR aml.id = apr.debit_move_id
                    LEFT JOIN res_currency rc ON aml.currency_id = rc.id
                    LEFT JOIN account_account_type aat ON aml.user_type_id = aat.id
                WHERE aat.type IN ('receivable', 'payable')
                GROUP BY aml.move_id
            ) AS sub
            WHERE id = sub.move_id
        """,
    )
    # Replace https://github.com/OCA/OpenUpgrade/blob/7a49881f87c0aa6ef2/addons/account/models/account_move.py#L352-L361
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line main
            SET debit_cash_basis = aml.debit * am.matched_percentage,
                credit_cash_basis = aml.credit * am.matched_percentage
            FROM
                account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN account_journal aj ON aml.journal_id = aj.id
            WHERE
                main.id = aml.id AND aj.type IN ('sale', 'purchase')
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line main
            SET debit_cash_basis = aml.debit,
                credit_cash_basis = aml.credit
            FROM
                account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN account_journal aj ON aml.journal_id = aj.id
            WHERE
                main.id = aml.id AND aj.type NOT IN ('sale', 'purchase')
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line
            SET balance_cash_basis = debit_cash_basis - credit_cash_basis
        """,
    )


def merge_invoice_journals(env, refund_journal_ids=None, journal_mapping=None):
    """Move invoices and entries from refund journals to normal ones.

    It can be used by other modules to complement this basic merging using
    the extra provided arguments.

    :param env: Odoo environment
    :param refund_journal_ids: Restrict the journals to merge to the passed
      ones.
    :param journal_mapping: Optional dictionary with refund journal IDs as keys
      and corresponding normal journal IDs as values for mapping the journals
      when there's no easy correspondence.
    """
    cr = env.cr
    journal_type_mapping = {
        'sale_refund': 'sale',
        'purchase_refund': 'purchase',
    }
    if journal_mapping is None:
        journal_mapping = {}
    # Add a column for storing target journal
    support_column = openupgrade.get_legacy_name('merged_journal_id')
    if not openupgrade.column_exists(cr, 'account_journal', support_column):
        openupgrade.logged_query(
            cr, "ALTER TABLE account_journal ADD %s INTEGER" % support_column,
        )
    for journal_type, new_journal_type in journal_type_mapping.iteritems():
        query = """
            SELECT id
            FROM account_journal
            WHERE %s = %%s
            """ % openupgrade.get_legacy_name('type')
        query_args = [journal_type, ]
        if refund_journal_ids:
            query += " AND id IN %s"
            query_args.append(tuple(refund_journal_ids))
        env.cr.execute(query, tuple(query_args))
        ids = [x[0] for x in env.cr.fetchall()]
        refund_journals = env['account.journal'].browse(ids)
        for refund_journal in refund_journals:
            if journal_mapping.get(refund_journal.id):
                normal_journal = env['account.journal'].browse(
                    journal_mapping[refund_journal.id]
                )
            else:
                normal_journal = env['account.journal'].search([
                    ('company_id', '=', refund_journal.company_id.id),
                    ('type', '=', new_journal_type),
                    ('id', '!=', refund_journal.id),
                ])
            # Is there only 1 'normal' journal for this company to move to?
            if len(normal_journal) > 1:
                continue
            # Change journal references for account objects
            tables = [
                'account_invoice',
                'account_move',
                'account_move_line',
            ]
            for table in tables:
                openupgrade.logged_query(
                    env.cr,
                    """
                    UPDATE %s
                    SET journal_id = %%s
                    WHERE journal_id = %%s
                    """ % table,
                    (normal_journal.id, refund_journal.id)
                )
            # for avoiding to be selected first when invoicing
            refund_journal.write({
                'show_on_dashboard': False,
                'sequence': 99999,
            })
            # update target journal in merged refund journal
            env.cr.execute(
                """UPDATE account_journal
                SET %s = %%s
                WHERE id = %%s
                """ % support_column,
                (normal_journal.id, refund_journal.id)
            )
            if refund_journal.sequence_id != normal_journal.sequence_id:
                # Fill refund sequence
                normal_journal.write({
                    'refund_sequence': True,
                    'refund_sequence_id': refund_journal.sequence_id.id,
                })


def update_account_invoice_date(cr):
    """Update invoice date from the period last date.

    NOTE: Invoices without linked journal entry won't be updated because they
    are supposed to be in draft or cancel state, so the date will be filled on
    normal validation workflow.
    """
    # Invoices with journal entries whose dates are in the same period
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice ai
        SET date = am.date
        FROM account_period ap,
             account_move am
        WHERE am.period_id = ap.id
            AND am.id = ai.move_id
            AND ai.date IS NULL
            AND am.date >= ap.date_start
            AND am.date <= ap.date_stop"""
    )
    # Invoices with journal entries whose dates are outside of forced period
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice ai
        SET date = ap.date_start
        FROM account_period ap,
             account_move am
        WHERE am.period_id = ap.id
            AND am.id = ai.move_id
            AND ai.date IS NULL
            AND (am.date < ap.date_start OR am.date > ap.date_stop)"""
    )


def update_move_date(cr):
    """Update journal entries date when the date is not inside the indicated
    period for respecting the accounting period on v9.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_move am
        SET date = ap.date_start
        FROM account_period ap
        WHERE am.period_id = ap.id
            AND (am.date < ap.date_start OR am.date > ap.date_stop)"""
    )
    # Synchronize move line dates afterwards
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_move_line aml
        SET date = am.date
        FROM account_move am
        WHERE am.id = aml.move_id
            AND am.date != aml.date"""
    )


def fill_bank_accounts(cr):
    """Fill new bank_account_id field on journals through the inverse
    reference on the bank accounts.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE account_journal aj
        SET bank_account_id = rpb.id
        FROM res_partner_bank rpb
        WHERE aj.type = 'bank'
        AND rpb.journal_id = aj.id"""
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    recompute_multicurrency_invoices(env)
    map_bank_state(cr)
    map_type_tax_use(cr)
    map_type_tax_use_template(cr)
    map_journal_state(cr)
    openupgrade_90.replace_account_types(env, account_type_map)
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

    # Value 'percentage_of_total' and 'percentage_of_balance' => 'percentage'
    cr.execute("""
    UPDATE account_operation_template SET amount_type = 'percentage'
    WHERE amount_type in ('percentage_of_total', 'percentage_of_balance')
    """)

    # Set up anglosaxon accounting
    cr.execute(
        "UPDATE res_company SET anglo_saxon_accounting = %s",
        (openupgrade.is_module_installed(cr, 'account_anglo_saxon'), ),
    )

    # deprecate accounts where active is False
    cr.execute("""
    UPDATE account_account SET deprecated = (active IS FALSE);
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
    move_view_accounts(env)
    account_internal_type(env)
    map_account_tax_type(cr)
    map_account_tax_template_type(cr)
    migrate_account_sequence_fiscalyear(cr)
    migrate_account_auto_fy_sequence(env)
    fill_move_taxes(env)
    fill_account_invoice_tax_taxes(env)
    fill_blacklisted_fields(cr)
    fast_compute_cash_basis(env)
    reset_blacklist_field_recomputation()
    fill_move_line_invoice(cr)
    merge_invoice_journals(env)
    update_account_invoice_date(cr)
    update_move_date(cr)
    fill_bank_accounts(cr)
    openupgrade.load_data(
        cr, 'account', 'migrations/9.0.1.1/noupdate_changes.xml',
    )
