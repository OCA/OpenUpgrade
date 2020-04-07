# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_account_reconcile_model_second_analytic_tag_rel_table(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_reconcile_model_second_analytic_tag_rel (
            account_reconcile_model_id, account_analytic_tag_id)
        SELECT account_reconcile_model_id, account_analytic_tag_id
        FROM account_reconcile_model_analytic_tag_rel
        """,
    )


def type_change_account_reconcile_model_taxes(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['account.reconcile.model'], 'account_reconcile_model',
        'second_tax_ids', openupgrade.get_legacy_name('second_tax_id')
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env['account.reconcile.model'], 'account_reconcile_model',
        'tax_ids', openupgrade.get_legacy_name('tax_id')
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env['account.reconcile.model.template'],
        'account_reconcile_model_template',
        'second_tax_ids', openupgrade.get_legacy_name('second_tax_id')
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env['account.reconcile.model.template'],
        'account_reconcile_model_template',
        'tax_ids', openupgrade.get_legacy_name('tax_id')
    )


def map_res_company_fiscalyear_last_month(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('fiscalyear_last_month'),
        'fiscalyear_last_month',
        [(x, '%s' % x) for x in range(1, 13, 1)],
        table='res_company',
    )


def fill_account_fiscal_position_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_fiscal_position afp
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = afp.create_uid AND
        afp.company_id is NULL
        """,
    )


def fill_account_account_type_internal_group(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_account_type
        SET internal_group = 'off_balance'
        WHERE internal_group IS NULL
        """,
    )


def map_account_journal_post_at_bank_rec(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('post_at_bank_rec'),
        'post_at',
        [(True, 'bank_rec')],
        table='account_journal',
    )


def fill_account_journal_restrict_mode_hash_table(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_journal
        SET restrict_mode_hash_table = TRUE
        WHERE {} != TRUE
        """.format(openupgrade.get_legacy_name('update_posted'))
    )


def map_account_payment_term_line_option_after_invoice_month(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('option'),
        'option',
        [('after_invoice_month', 'day_following_month')],
        table='account_payment_term_line',
    )


def archive_account_tax_type_tax_use_adjustment(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_tax
        SET active = FALSE, type_tax_use='none'
        WHERE type_tax_use = 'adjustment'
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_tax_template
        SET active = FALSE, type_tax_use='none'
        WHERE type_tax_use = 'adjustment'
        """,
    )


def fill_account_journal_invoice_reference_type(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_journal aj
        SET invoice_reference_type = CASE
          WHEN rc.{irt} = 'invoice_number' THEN 'invoice'
          ELSE rc.{irt} END
        FROM res_company rc
        WHERE aj.company_id = rc.id AND rc.{irt} IS NOT NULL
        """.format(irt=openupgrade.get_legacy_name('invoice_reference_type'))
    )


def migration_invoice_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET (message_main_attachment_id, access_token, name, date, ref,
        narration, type, journal_id, company_id, currency_id, partner_id,
        commercial_partner_id, amount_untaxed, amount_tax, amount_total,
        amount_residual, amount_untaxed_signed, amount_tax_signed,
        amount_total_signed, amount_residual_signed, fiscal_position_id,
        invoice_user_id, state, invoice_payment_state, invoice_date,
        invoice_date_due, invoice_payment_ref, invoice_sent, invoice_origin,
        invoice_payment_term_id, invoice_partner_bank_id, invoice_incoterm_id,
        invoice_source_email, invoice_partner_display_name,
        invoice_cash_rounding_id, create_uid, create_date, write_uid,
        write_date) = (
        ai.message_main_attachment_id, ai.access_token,
        COALESCE(ai.number, ai.move_name, am.name), COALESCE(ai.date, am.date),
        ai.reference, ai.comment, ai.type, ai.journal_id, ai.company_id,
        ai.currency_id, ai.partner_id, ai.commercial_partner_id,
        ai.amount_untaxed, ai.amount_tax, ai.amount_total, ai.residual,
        ai.amount_untaxed_signed, ai.amount_tax_company_signed, COALESCE(
        ai.amount_total_company_signed, ai.amount_total_signed),
        COALESCE(ai.residual_company_signed, ai.residual_signed),
        ai.fiscal_position_id, ai.user_id, CASE WHEN ai.state = 'cancel'
        THEN 'cancel' ELSE 'posted' END, CASE WHEN ai.state IN (
        'in_payment', 'paid') THEN ai.state ELSE 'not_paid' END,
        ai.date_invoice, ai.date_due, ai.name, ai.sent, ai.origin,
        ai.payment_term_id, ai.partner_bank_id, ai.incoterm_id,
        ai.source_email, ai.vendor_display_name, ai.cash_rounding_id,
        ai.create_uid, ai.create_date, ai.write_uid, ai.write_date)
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id AND ai.state not in ('draft', 'cancel')
        RETURNING am.old_invoice_id, am.id
        """,
    )
    ids1 = env.cr.fetchall()
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET exclude_from_invoice_tab = TRUE
        FROM account_move am
        JOIN account_invoice ai ON am.old_invoice_id = ai.id
        LEFT JOIN account_account aa ON ai.account_id = aa.id
        WHERE aml.{} IS NOT NULL AND aml.move_id = am.id AND (((
            aa.internal_type in ('receivable', 'payable') OR
            aml.tax_line_id IS NOT NULL) AND ai.state not in (
            'draft', 'cancel')) OR ai.state in ('draft', 'cancel'))
        """.format(openupgrade.get_legacy_name('id'))
    )
    env.cr.execute(
        "ALTER TABLE account_move_line DROP COLUMN {}".format(
            openupgrade.get_legacy_name('id'))
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move (message_main_attachment_id, access_token,
        name, date, ref, narration, type, journal_id, company_id, currency_id,
        partner_id, commercial_partner_id, amount_untaxed, amount_tax,
        amount_total, amount_residual, amount_untaxed_signed,
        amount_tax_signed, amount_total_signed, amount_residual_signed,
        fiscal_position_id, invoice_user_id, state, invoice_payment_state,
        invoice_date, invoice_date_due, invoice_payment_ref, invoice_sent,
        invoice_origin, invoice_payment_term_id, invoice_partner_bank_id,
        invoice_incoterm_id, invoice_source_email,
        invoice_partner_display_name, invoice_cash_rounding_id, old_invoice_id,
        create_uid, create_date, write_uid, write_date)
        SELECT message_main_attachment_id, access_token,
        COALESCE(number, move_name, name, '/'), COALESCE(date, date_invoice,
        write_date), reference, comment, type, journal_id, company_id,
        currency_id, partner_id, commercial_partner_id, amount_untaxed,
        amount_tax, amount_total, residual, amount_untaxed_signed,
        amount_tax_company_signed, amount_total_company_signed,
        residual_company_signed, fiscal_position_id, user_id,
        state, 'not_paid', date_invoice, date_due, name, sent, origin,
        payment_term_id, partner_bank_id, incoterm_id, source_email,
        vendor_display_name, cash_rounding_id, id, create_uid, create_date,
        write_uid, write_date
        FROM account_invoice ai
        WHERE ai.state in ('draft', 'cancel')
        RETURNING old_invoice_id, id""",
    )
    ids2 = env.cr.fetchall()
    if ids1 or ids2:
        _move_model_in_data(
            env, ids1 + ids2, 'account.invoice', 'account.move')
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, account_id,
        sequence, name, quantity, price_unit, discount,
        price_subtotal, price_total, currency_id, partner_id, product_uom_id,
        product_id, analytic_account_id, display_type, is_rounding_line,
        move_id, old_invoice_line_id, create_uid, create_date, write_uid,
        write_date)
        SELECT ail.company_id, ail.account_id, ail.sequence, ail.name,
        ail.quantity, ail.price_unit, ail.discount, ail.price_subtotal,
        ail.price_total, ail.currency_id, ail.partner_id, ail.uom_id,
        ail.product_id, ail.account_analytic_id, ail.display_type,
        ail.is_rounding_line, COALESCE(ai.move_id, am.id), ail.id,
        ail.create_uid, ail.create_date, ail.write_uid, ail.write_date
        FROM account_invoice_line ail
        LEFT JOIN account_invoice ai ON ail.invoice_id = ai.id
        LEFT JOIN account_move am ON am.old_invoice_id = ai.id
        LEFT JOIN account_account aa ON ai.account_id = aa.id
        WHERE COALESCE(ai.move_id, am.id) IS NOT NULL AND
            aa.internal_type in ('receivable', 'payable')""",
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, account_id,
        sequence, name, price_unit, currency_id, tax_base_amount,
        tax_line_id, analytic_account_id, move_id, old_invoice_tax_id,
        create_uid, create_date, write_uid, write_date)
        SELECT ait.company_id, ait.account_id, ait.sequence, ait.name,
        ait.amount, ait.currency_id, ait.base, ait.tax_id,
        ait.account_analytic_id, COALESCE(ai.move_id, am.id),
        ait.id, ait.create_uid, ait.create_date, ait.write_uid, ait.write_date
        FROM account_invoice_tax ait
        LEFT JOIN account_invoice ai ON ait.invoice_id = ai.id
        LEFT JOIN account_move am ON am.old_invoice_id = ai.id
        WHERE COALESCE(ai.move_id, am.id) IS NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice_payment_rel aipr
        SET invoice_id = am.id
        FROM account_move am
        WHERE am.old_invoice_id = aipr.invoice_id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_analytic_tag_account_move_line_rel (
            account_move_line_id, account_analytic_tag_id)
        SELECT aml.id, aatailr.account_analytic_tag_id
        FROM account_analytic_tag_account_invoice_line_rel aatailr
        JOIN account_move_line aml
        ON aml.old_invoice_line_id = aatailr.account_invoice_line_id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_analytic_tag_account_move_line_rel (
            account_move_line_id, account_analytic_tag_id)
        SELECT aml.id, aataitr.account_analytic_tag_id
        FROM account_analytic_tag_account_invoice_tax_rel aataitr
        JOIN account_move_line aml
        ON aml.old_invoice_tax_id = aataitr.account_invoice_tax_id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line_account_tax_rel (
            account_move_line_id, account_tax_id)
        SELECT aml.id, ailt.tax_id
        FROM account_invoice_line_tax ailt
        JOIN account_move_line aml
        ON aml.old_invoice_line_id = ailt.invoice_line_id
        """,
    )


def migration_voucher_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET (message_main_attachment_id, name, date, ref, narration, type,
        journal_id, company_id, currency_id, partner_id, amount_tax,
        amount_total, state, invoice_payment_state, invoice_date,
        invoice_date_due, invoice_payment_ref, create_uid, create_date,
        write_uid, write_date) = (
        av.message_main_attachment_id, COALESCE(av.number, am.name),
        COALESCE(av.date, am.date), av.reference, av.narration,
        CASE WHEN av.voucher_type = 'purchase' THEN 'in_receipt'
        ELSE 'out_receipt' END, av.journal_id, av.company_id,
        av.currency_id, av.partner_id, av.tax_amount, av.amount,
        CASE WHEN av.state = 'proforma' THEN 'posted' ELSE av.state END,
        CASE WHEN av.state = 'cancel' THEN 'not_paid' ELSE 'paid' END,
        av.account_date, av.date_due, av.name, av.create_uid, av.create_date,
        av.write_uid, av.write_date)
        FROM account_voucher av
        WHERE am.old_voucher_id = av.id AND av.state not in (
            'draft', 'cancel', 'proforma')
        RETURNING am.old_voucher_id, am.id
        """,
    )
    ids1 = env.cr.fetchall()
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move (message_main_attachment_id, name, date,
        ref, narration, type, journal_id, company_id, currency_id, partner_id,
        amount_tax, amount_total, state, invoice_payment_state, invoice_date,
        invoice_date_due, invoice_payment_ref, old_voucher_id,
        create_uid, create_date, write_uid, write_date)
        SELECT message_main_attachment_id, COALESCE(number, '/'), date,
        reference, narration, CASE WHEN voucher_type = 'purchase'
        THEN 'in_receipt' ELSE 'out_receipt' END, journal_id, company_id,
        currency_id, partner_id, tax_amount, amount, state, 'not_paid',
        account_date, date_due, name, id, create_uid, create_date, write_uid,
        write_date
        FROM account_voucher av
        WHERE av.state in ('draft', 'cancel', 'proforma')
        RETURNING old_voucher_id, id""",
    )
    ids2 = env.cr.fetchall()
    if ids1 or ids2:
        _move_model_in_data(
            env, ids1 + ids2, 'account.voucher', 'account.move')
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, account_id,
        sequence, name, quantity, price_unit, price_subtotal,
        product_id, analytic_account_id, move_id, old_voucher_line_id,
        create_uid, create_date, write_uid, write_date)
        SELECT avl.company_id, avl.account_id, avl.sequence, avl.name,
        avl.quantity, avl.price_unit, avl.price_subtotal, avl.product_id,
        avl.account_analytic_id, COALESCE(av.move_id, am.id), avl.id,
        avl.create_uid, avl.create_date, avl.write_uid, avl.write_date
        FROM account_voucher_line avl
        LEFT JOIN account_voucher av ON avl.voucher_id = av.id
        LEFT JOIN account_move am ON am.old_voucher_id = av.id
        WHERE COALESCE(av.move_id, am.id) IS NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_analytic_tag_account_move_line_rel (
        account_move_line_id, account_analytic_tag_id)
        SELECT aml.id, aatavlr.account_analytic_tag_id
        FROM account_analytic_tag_account_voucher_line_rel aatavlr
        JOIN account_move_line aml
        ON aml.old_voucher_line_id = aatavlr.account_voucher_line_id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line_account_tax_rel (
        account_move_line_id, account_tax_id)
        SELECT aml.id, atavlr.account_tax_id
        FROM account_tax_account_voucher_line_rel atavlr
        JOIN account_move_line aml
        ON aml.old_voucher_line_id = atavlr.account_voucher_line_id
        """,
    )


def _move_model_in_data(env, ids_map, old_model, new_model):
    renames = [
        ('mail_message', 'model', 'res_id'),
        ('mail_followers', 'res_model', 'res_id'),
        ('ir_attachment', 'res_model', 'res_id'),
        ('mail_activity', 'res_model', 'res_id'),
        ('ir_model_data', 'model', 'res_id'),
    ]
    for old_id, new_id in ids_map:
        for rename in renames:
            openupgrade.logged_query(
                env.cr, """
                UPDATE {table}
                SET {field1} = '{new_value1}', {field2} = {new_value2}
                WHERE {field1} = '{old_value1}' AND {field2} = {old_value2}
                """.format(
                    table=rename[0], field1=rename[1], field2=rename[2],
                    old_value1=old_model, new_value1=new_model,
                    old_value2=old_id, new_value2=new_id,
                )
            )


def fill_account_move_type(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move
        SET type = 'entry'
        WHERE type IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET account_internal_type = aat.type
        FROM account_account aa
        JOIN account_account_type aat ON aa.user_type_id = aat.id
        WHERE aml.account_id = aa.id AND aml.account_internal_type IS NULL
        """,
    )


def fill_account_move_currency_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET currency_id = COALESCE(am_rel.cur1, am_rel.cur2)
        FROM (SELECT am1.id, aj.currency_id as cur1, rc.currency_id as cur2
          FROM account_move am1
          LEFT JOIN account_journal aj ON aj.id = am1.journal_id
          LEFT JOIN res_company rc ON rc.id = aj.company_id) am_rel
        WHERE am.id = am_rel.id AND am.currency_id IS NULL
        """,
    )


def fill_account_move_line_parent_state(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET parent_state = am.state
        FROM account_move am
        WHERE am.id = aml.move_id AND
        (aml.exclude_from_invoice_tab IS NOT TRUE OR am.state = 'cancel')""",
    )


def fill_account_move_line_move_name(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET move_name = am.name
        FROM account_move am
        WHERE am.id = aml.move_id AND aml.move_name != am.name""",
    )


def fill_res_partner_ranks(env):
    # customer_rank
    openupgrade.logged_query(
        env.cr, """
        UPDATE res_partner rp
        SET customer_rank = rel.customer_rank
        FROM (SELECT am.partner_id, count(am.id) as customer_rank
            FROM account_move am
            WHERE am.state != 'draft' AND left(am.type,4) = 'out_' AND
                am.partner_id IS NOT NULL
            GROUP BY am.partner_id) rel
        WHERE rel.partner_id = rp.id""",
    )
    # supplier_rank
    openupgrade.logged_query(
        env.cr, """
        UPDATE res_partner rp
        SET supplier_rank = rel.supplier_rank
        FROM (SELECT am.partner_id, count(am.id) as supplier_rank
            FROM account_move am
            JOIN res_partner rp ON am.partner_id = rp.id
            WHERE am.state != 'draft' AND left(am.type,3) = 'in_' AND
                am.partner_id IS NOT NULL
            GROUP BY am.partner_id) rel
        WHERE rel.partner_id = rp.id""",
    )


def try_to_fill_account_account_tag_country_id(env):
    # NOTE: the filling is not exhaustive
    # from account.account
    openupgrade.logged_query(
        env.cr, """
        WITH select_tags AS (
            SELECT aat.id
            FROM account_account_tag aat
            JOIN account_account_account_tag aaat ON (
                aat.applicability = 'accounts' AND aat.country_id IS NULL
                AND aaat.account_account_tag_id = aat.id)
            JOIN account_account aa ON aaat.account_account_id = aa.id
            JOIN res_company rc ON aa.company_id = rc.id
            JOIN res_partner rp ON (
                rc.partner_id = rp.id AND rp.country_id IS NOT NULL)
            GROUP BY aat.id
            HAVING count(DISTINCT rp.country_id) = 1
        )
        UPDATE account_account_tag aat
        SET country_id = rp.country_id
        FROM account_account_account_tag aaat
        JOIN select_tags sel ON sel.id = aaat.account_account_tag_id
        JOIN account_account aa ON aaat.account_account_id = aa.id
        JOIN res_company rc ON aa.company_id = rc.id
        JOIN res_partner rp ON rc.partner_id = rp.id
        WHERE aat.applicability = 'accounts' AND aat.country_id IS NULL
            AND aaat.account_account_tag_id = aat.id
            AND rp.country_id IS NOT NULL""",
    )
    # from account.tax
    openupgrade.logged_query(
        env.cr, """
        WITH select_tags AS (
            SELECT aat.id
            FROM account_account_tag aat
            JOIN account_tax_account_tag atat ON (
                aat.applicability = 'taxes' AND aat.country_id IS NULL
                AND atat.account_account_tag_id = aat.id)
            JOIN account_tax t ON atat.account_tax_id = t.id
            JOIN res_company rc ON t.company_id = rc.id
            JOIN res_partner rp ON (
                rc.partner_id = rp.id AND rp.country_id IS NOT NULL)
            GROUP BY aat.id
            HAVING count(DISTINCT rp.country_id) = 1
        )
        UPDATE account_account_tag aat
        SET country_id = rp.country_id
        FROM account_tax_account_tag atat
        JOIN select_tags sel ON sel.id = atat.account_account_tag_id
        JOIN account_tax t ON atat.account_tax_id = t.id
        JOIN res_company rc ON t.company_id = rc.id
        JOIN res_partner rp ON rc.partner_id = rp.id
        WHERE aat.applicability = 'taxes' AND aat.country_id IS NULL
            AND atat.account_account_tag_id = aat.id
            AND rp.country_id IS NOT NULL""",
    )


def create_account_tax_repartition_lines(env):
    # account_tax_repartition_line
    all_taxes = env['account.tax'].with_context(active_test=False).search([])
    complete_taxes = env['account.tax.repartition.line'].search(
        [('tax_id', '!=', False)]).mapped('tax_id')
    tax_ids = (all_taxes - complete_taxes).ids
    if tax_ids:
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line (
                account_id, company_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type, sequence,
                create_uid, create_date, write_uid, write_date)
            SELECT NULL, company_id, 100, id, NULL, 'base', 1,
                create_uid, create_date, write_uid, write_date
            FROM account_tax
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line (
                account_id, company_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type, sequence,
                create_uid, create_date, write_uid, write_date)
            SELECT CASE WHEN tax_exigibility = 'on_payment'
                THEN cash_basis_account_id ELSE account_id END,
                company_id, 100, id, NULL, 'tax', 1,
                create_uid, create_date, write_uid, write_date
            FROM account_tax
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line (
                account_id, company_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type, sequence,
                create_uid, create_date, write_uid, write_date)
            SELECT NULL, company_id, 100, NULL, id, 'base', 1,
                create_uid, create_date, write_uid, write_date
            FROM account_tax
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line (
                account_id, company_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type, sequence,
                create_uid, create_date, write_uid, write_date)
            SELECT CASE WHEN tax_exigibility = 'on_payment'
                THEN cash_basis_account_id ELSE refund_account_id END,
                company_id, 100, NULL, id, 'tax', 1,
                create_uid, create_date, write_uid, write_date
            FROM account_tax
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_tax at
        SET cash_basis_transition_account_id = at.account_id
        WHERE at.tax_exigibility = 'on_payment'
            AND at.cash_basis_transition_account_id IS NULL"""
    )

    # account_tax_repartition_line_template
    all_taxes = env['account.tax.template'].with_context(
        active_test=False).search([])
    complete_taxes = env['account.tax.repartition.line.template'].search(
        [('invoice_tax_id', '!=', False)]).mapped('invoice_tax_id') | env[
        'account.tax.repartition.line.template'].search(
        [('refund_tax_id', '!=', False)]).mapped('refund_tax_id')
    tax_ids = (all_taxes - complete_taxes).ids
    if tax_ids:
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line_template (
                account_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type,
                create_uid, create_date, write_uid, write_date)
            SELECT NULL, 100, id, NULL, 'base',
                create_uid, create_date, write_uid, write_date
            FROM account_tax_template
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line_template (
                account_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type,
                create_uid, create_date, write_uid, write_date)
            SELECT CASE WHEN tax_exigibility = 'on_payment'
                THEN cash_basis_account_id ELSE account_id END,
                100, id, NULL, 'tax',
                create_uid, create_date, write_uid, write_date
            FROM account_tax_template
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line_template (
                account_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type,
                create_uid, create_date, write_uid, write_date)
            SELECT NULL, 100, NULL, id, 'base',
                create_uid, create_date, write_uid, write_date
            FROM account_tax_template
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_tax_repartition_line_template (
                account_id, factor_percent, invoice_tax_id,
                refund_tax_id, repartition_type,
                create_uid, create_date, write_uid, write_date)
            SELECT CASE WHEN tax_exigibility = 'on_payment'
                THEN cash_basis_account_id ELSE refund_account_id END,
                100, NULL, id, 'tax',
                create_uid, create_date, write_uid, write_date
            FROM account_tax_template
            WHERE id IN %s""", (tuple(tax_ids), ),
        )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_tax_template att
        SET cash_basis_transition_account_id = att.account_id
        WHERE att.tax_exigibility = 'on_payment'
            AND att.cash_basis_transition_account_id IS NULL"""
    )


def move_tags_from_taxes_to_repartition_lines(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_tax_repartition_line_rel (
            account_tax_repartition_line_id, account_account_tag_id)
        SELECT atrl.id, atat.account_account_tag_id
        FROM account_tax_account_tag atat
        JOIN account_tax_repartition_line atrl ON
            (atat.account_tax_id = atrl.invoice_tax_id OR
             atat.account_tax_id = atrl.refund_tax_id)"""
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_tax_repartition_financial_tags (
            account_tax_repartition_line_template_id, account_account_tag_id)
        SELECT atrlt.id, aatattr.account_account_tag_id
        FROM account_account_tag_account_tax_template_rel aatattr
        JOIN account_tax_repartition_line_template atrlt ON
            (aatattr.account_tax_template_id = atrlt.invoice_tax_id OR
             aatattr.account_tax_template_id = atrlt.refund_tax_id)"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_reconcile_model_second_analytic_tag_rel_table(env)
    type_change_account_reconcile_model_taxes(env)
    map_res_company_fiscalyear_last_month(env)
    fill_account_fiscal_position_company_id(env)
    fill_account_account_type_internal_group(env)
    map_account_journal_post_at_bank_rec(env)
    fill_account_journal_restrict_mode_hash_table(env)
    map_account_payment_term_line_option_after_invoice_month(env)
    archive_account_tax_type_tax_use_adjustment(env)
    fill_account_journal_invoice_reference_type(env)
    migration_invoice_moves(env)
    if openupgrade.table_exists(env.cr, 'account_voucher'):
        migration_voucher_moves(env)
    fill_account_move_type(env)
    fill_account_move_currency_id(env)
    fill_account_move_line_parent_state(env)
    fill_account_move_line_move_name(env)
    fill_res_partner_ranks(env)
    try_to_fill_account_account_tag_country_id(env)
    create_account_tax_repartition_lines(env)
    move_tags_from_taxes_to_repartition_lines(env)
    openupgrade.load_data(
        env.cr, "account", "migrations/13.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, 'account', [
            'email_template_edi_invoice',
            'mail_template_data_payment_receipt',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "account_voucher.mt_voucher_state_change",
            "account.model_account_invoice_action_share",
            "ir.rule: account.account_invoice_line_comp_rule",
            "ir.rule: account.invoice_comp_rule",
            "ir.rule: account_voucher.voucher_comp_rule",
            "ir.rule: account_voucher.voucher_line_comp_rule",
            "account.account_payment_term_net",
            "account.reconciliation_model_default_rule",
        ]
    )
