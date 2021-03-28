# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql


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
        RETURNING id
        """.format(openupgrade.get_legacy_name('update_posted'))
    )
    ids = [x[0] for x in env.cr.fetchall()]
    if ids:
        env['account.journal'].browse(ids)._create_secure_sequence(
            ['secure_sequence_id'])


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
    # Transfer fields from invoices to linked moves
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
        CASE WHEN ai.type IN ('in_invoice', 'in_refund')
        THEN -ai.amount_untaxed_signed ELSE ai.amount_untaxed_signed END,
        CASE WHEN ai.type IN ('in_invoice', 'in_refund')
        THEN -ai.amount_tax_company_signed ELSE ai.amount_tax_company_signed END,
        CASE WHEN ai.type IN ('in_invoice', 'in_refund')
        THEN -COALESCE(ai.amount_total_company_signed, ai.amount_total_signed)
        ELSE COALESCE(ai.amount_total_company_signed, ai.amount_total_signed) END,
        CASE WHEN ai.type IN ('in_invoice', 'in_refund')
        THEN -COALESCE(ai.residual_company_signed, ai.residual_signed)
        ELSE COALESCE(ai.residual_company_signed, ai.residual_signed) END,
        ai.fiscal_position_id, ai.user_id, 'posted', CASE WHEN ai.state IN (
        'in_payment', 'paid') THEN ai.state ELSE 'not_paid' END,
        ai.date_invoice, ai.date_due, ai.name, ai.sent, ai.origin,
        ai.payment_term_id, ai.partner_bank_id, ai.incoterm_id,
        ai.source_email, ai.vendor_display_name, ai.cash_rounding_id,
        ai.create_uid, ai.create_date, ai.write_uid, ai.write_date)
        FROM account_invoice ai
        WHERE am.id = ai.move_id AND ai.state not in ('draft', 'cancel')
        RETURNING ai.id, am.id
        """,
    )
    ids1 = env.cr.fetchall()
    # Insert moves for draft or canceled invoices
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
        amount_tax, amount_total, residual,
        CASE WHEN type IN ('in_invoice', 'in_refund')
        THEN -amount_untaxed_signed ELSE amount_untaxed_signed END,
        CASE WHEN type IN ('in_invoice', 'in_refund')
        THEN -amount_tax_company_signed ELSE amount_tax_company_signed END,
        CASE WHEN type IN ('in_invoice', 'in_refund')
        THEN -amount_total_company_signed ELSE amount_total_company_signed END,
        CASE WHEN type IN ('in_invoice', 'in_refund')
        THEN -residual_company_signed ELSE residual_company_signed END,
        fiscal_position_id, user_id,
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
    # Not Draft or Cancel Invoice Lines
    # 1st: update the ungrouped ones
    query = """
        UPDATE account_move_line aml
        SET exclude_from_invoice_tab = FALSE, sequence = ail.sequence,
        price_unit = ail.price_unit, discount = ail.discount, price_subtotal = ail.price_subtotal,
        price_total = ail.price_total, display_type = ail.display_type,
        is_rounding_line = ail.is_rounding_line, old_invoice_line_id = ail.id,
        create_uid = ail.create_uid, create_date = ail.create_date
        FROM account_invoice_line ail
            JOIN account_invoice ai ON ail.invoice_id = ai.id AND ai.state NOT IN ('draft', 'cancel')
            JOIN account_move am ON ail.invoice_id = am.old_invoice_id
            JOIN res_company rc ON ai.company_id = rc.id
        """
    # We assign to the move lines information from the matching invoice line.
    # Everything that has a tax_line_id (originator tax) is by definition originating
    # from the invoice taxes, not from invoice lines.
    # The move lines that have a receivable or payable account (the same as the one
    # from the invoice) are not associated to any invoice line.
    minimal_where = """
        WHERE am.id = aml.move_id
            AND aml.tax_line_id IS NULL
            AND aml.account_id <> ai.account_id
            AND ail.quantity = aml.quantity
            AND ((ail.product_id IS NULL AND aml.product_id IS NULL) OR ail.product_id = aml.product_id)
            AND ((ail.uom_id IS NULL AND aml.product_uom_id IS NULL) OR ail.uom_id = aml.product_uom_id)
        """
    # Try first with a stricter criteria for matching invoice lines with account move lines
    openupgrade.logged_query(
        env.cr, query + minimal_where + """
            AND ail.account_id = aml.account_id
            AND ai.commercial_partner_id = aml.partner_id
            AND ((ail.account_analytic_id IS NULL AND aml.analytic_account_id IS NULL)
                OR ail.account_analytic_id = aml.analytic_account_id)
        RETURNING aml.id""",
    )
    aml_ids = tuple(x[0] for x in env.cr.fetchall())
    # Try now with a more relaxed criteria, as it's possible that users change some data on amls
    openupgrade.logged_query(
        env.cr, query + minimal_where + """
            AND aml.old_invoice_line_id IS NULL
            AND rc.anglo_saxon_accounting IS DISTINCT FROM TRUE
        RETURNING aml.id""",
    )
    aml_ids += tuple(x[0] for x in env.cr.fetchall())
    # 2st: exclude from invoice_tab the grouped ones, and create a new separated ones
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET exclude_from_invoice_tab = TRUE, sequence = ail.sequence,
        name = '(OLD GROUPED ITEM)' || aml.name,
        create_uid = ail.create_uid, create_date = ail.create_date
        FROM account_invoice_line ail
            JOIN account_invoice ai ON ail.invoice_id = ai.id AND ai.state NOT IN ('draft', 'cancel')
            JOIN account_move am ON ail.invoice_id = am.old_invoice_id
        WHERE am.id = aml.move_id AND ail.company_id = aml.company_id AND ail.account_id = aml.account_id
            AND ail.partner_id = aml.partner_id
            AND ((ail.product_id IS NULL AND aml.product_id IS NULL) OR ail.product_id = aml.product_id)
            AND ((ail.uom_id IS NULL AND aml.product_uom_id IS NULL) OR ail.uom_id = aml.product_uom_id)
            AND ((ail.account_analytic_id IS NULL AND aml.analytic_account_id IS NULL)
                OR ail.account_analytic_id = aml.analytic_account_id)
            AND aml.tax_line_id IS NULL
            AND aml.old_invoice_line_id IS NULL
        RETURNING aml.id""",
    )
    aml_ids2 = tuple(x[0] for x in env.cr.fetchall())
    if aml_ids2:
        openupgrade.logged_query(
            env.cr, """
            SELECT ail.id
            FROM account_invoice_line ail
                JOIN account_invoice ai ON ail.invoice_id = ai.id AND ai.state NOT IN ('draft', 'cancel')
                JOIN account_move am ON ail.invoice_id = am.old_invoice_id
                JOIN account_move_line aml ON am.id = aml.move_id
            WHERE ail.company_id = aml.company_id AND ail.account_id = aml.account_id
                AND ail.partner_id = aml.partner_id
                AND ((ail.product_id IS NULL AND aml.product_id IS NULL) OR ail.product_id = aml.product_id)
                AND ((ail.uom_id IS NULL AND aml.product_uom_id IS NULL) OR ail.uom_id = aml.product_uom_id)
                AND ((ail.account_analytic_id IS NULL AND aml.analytic_account_id IS NULL)
                    OR ail.account_analytic_id = aml.analytic_account_id)
                AND aml.tax_line_id IS NULL
                AND aml.id IN %s""", (aml_ids2, ),
        )
        ail_ids = tuple(x[0] for x in env.cr.fetchall())
        if ail_ids:
            openupgrade.logged_query(
                env.cr, """
                INSERT INTO account_move_line (company_id, journal_id, account_id,
                exclude_from_invoice_tab, sequence, name, quantity, price_unit, discount,
                price_subtotal, price_total, company_currency_id, currency_id, partner_id, product_uom_id,
                product_id, analytic_account_id, display_type, is_rounding_line,
                move_id, old_invoice_line_id, date, create_uid, create_date, write_uid,
                write_date)
                SELECT ail.company_id, am.journal_id, ail.account_id, FALSE, ail.sequence, ail.name,
                ail.quantity, ail.price_unit, ail.discount, ail.price_subtotal,
                ail.price_total, rc.currency_id, CASE WHEN rc.currency_id != ail.currency_id
                THEN ail.currency_id ELSE NULL END, ail.partner_id, ail.uom_id,
                ail.product_id, ail.account_analytic_id, ail.display_type,
                ail.is_rounding_line, COALESCE(ai.move_id, am.id), ail.id, COALESCE(ai.date, ai.date_invoice),
                ail.create_uid, ail.create_date, ail.write_uid, ail.write_date
                FROM account_invoice_line ail
                    JOIN account_invoice ai ON ail.invoice_id = ai.id
                    JOIN account_move am ON am.old_invoice_id = ai.id
                    LEFT JOIN res_company rc ON ail.company_id = rc.id
                WHERE ail.id IN %s
                RETURNING id""", (ail_ids, ),
            )
            aml_ids += tuple(x[0] for x in env.cr.fetchall())
    # 3rd: assure they have a corresponding old_invoice_line_id. If not, exclude them from invoice tab
    if aml_ids:
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_move_line
            SET exclude_from_invoice_tab = TRUE
            WHERE old_invoice_line_id IS NULL""",
        )
    # Draft or Cancel Invoice Lines
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, journal_id, account_id,
        exclude_from_invoice_tab, sequence, name, quantity, price_unit, discount,
        price_subtotal, price_total, company_currency_id, currency_id, partner_id, product_uom_id,
        product_id, analytic_account_id, display_type, is_rounding_line,
        move_id, old_invoice_line_id, date, create_uid, create_date, write_uid,
        write_date)
        SELECT ail.company_id, am.journal_id, ail.account_id, FALSE, ail.sequence, ail.name,
        ail.quantity, ail.price_unit, ail.discount, ail.price_subtotal,
        ail.price_total, rc.currency_id, CASE WHEN rc.currency_id != ail.currency_id
        THEN ail.currency_id ELSE NULL END, ail.partner_id, ail.uom_id,
        ail.product_id, ail.account_analytic_id, ail.display_type,
        ail.is_rounding_line, COALESCE(ai.move_id, am.id), ail.id, COALESCE(ai.date, ai.date_invoice),
        ail.create_uid, ail.create_date, ail.write_uid, ail.write_date
        FROM account_invoice_line ail
            JOIN account_invoice ai ON ail.invoice_id = ai.id AND ai.state IN ('draft', 'cancel')
            LEFT JOIN res_company rc ON ail.company_id = rc.id
        LEFT JOIN account_move am ON am.old_invoice_id = ai.id
        LEFT JOIN account_account aa ON ai.account_id = aa.id
        WHERE am.id IS NOT NULL AND
            aa.internal_type in ('receivable', 'payable')""",
    )
    # Not Draft or Cancel Invoice Taxes
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET exclude_from_invoice_tab = TRUE, sequence = ait.sequence, price_unit = ait.amount,
        old_invoice_tax_id = ait.id,
        create_uid = ait.create_uid, create_date = ait.create_date
        FROM account_invoice_tax ait
            JOIN account_invoice ai ON ait.invoice_id = ai.id AND ai.state NOT IN ('draft', 'cancel')
            JOIN account_move am ON ait.invoice_id = am.old_invoice_id
        WHERE am.id = aml.move_id AND ait.company_id = aml.company_id AND ait.account_id = aml.account_id
            AND ait.tax_id = aml.tax_line_id
            AND ((ait.account_analytic_id IS NULL AND aml.analytic_account_id IS NULL)
            OR ait.account_analytic_id = aml.analytic_account_id)""",
    )
    # Draft or Cancel Invoice Taxes
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, journal_id, account_id,
        sequence, name, price_unit, currency_id, tax_base_amount,
        tax_line_id, analytic_account_id, move_id, old_invoice_tax_id,
        exclude_from_invoice_tab, parent_state, quantity, partner_id, date,
        create_uid, create_date, write_uid, write_date)
        SELECT ait.company_id, am.journal_id, ait.account_id, ait.sequence, ait.name,
        ait.amount, ait.currency_id, ait.base, ait.tax_id,
        ait.account_analytic_id, COALESCE(ai.move_id, am.id),
        ait.id, TRUE, am.state, 1.0, ai.commercial_partner_id, COALESCE(ai.date, ai.date_invoice),
        ait.create_uid, ait.create_date, ait.write_uid, ait.write_date
        FROM account_invoice_tax ait
        JOIN account_invoice ai ON ait.invoice_id = ai.id AND ai.state IN ('draft', 'cancel')
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
    # Relink analytic tags
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_analytic_tag_account_move_line_rel (
            account_move_line_id, account_analytic_tag_id)
        SELECT aml.id, aatailr.account_analytic_tag_id
        FROM account_analytic_tag_account_invoice_line_rel aatailr
        JOIN account_move_line aml
        ON aml.old_invoice_line_id = aatailr.account_invoice_line_id
        LEFT JOIN account_analytic_tag_account_move_line_rel aatamlr
        ON aml.id = aatamlr.account_move_line_id AND aatailr.account_analytic_tag_id = aatamlr.account_analytic_tag_id
        WHERE aatamlr.account_analytic_tag_id IS NULL
        ON CONFLICT DO NOTHING""",
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_analytic_tag_account_move_line_rel (
            account_move_line_id, account_analytic_tag_id)
        SELECT aml.id, aataitr.account_analytic_tag_id
        FROM account_analytic_tag_account_invoice_tax_rel aataitr
        JOIN account_move_line aml
        ON aml.old_invoice_tax_id = aataitr.account_invoice_tax_id
        LEFT JOIN account_analytic_tag_account_move_line_rel aatamlr
        ON aml.id = aatamlr.account_move_line_id AND aataitr.account_analytic_tag_id = aatamlr.account_analytic_tag_id
        WHERE aatamlr.account_analytic_tag_id IS NULL
        ON CONFLICT DO NOTHING""",
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line_account_tax_rel (
            account_move_line_id, account_tax_id)
        SELECT aml.id, ailt.tax_id
        FROM account_invoice_line_tax ailt
        JOIN account_move_line aml
        ON aml.old_invoice_line_id = ailt.invoice_line_id
        LEFT JOIN account_move_line_account_tax_rel amlatr
        ON aml.id = amlatr.account_move_line_id AND ailt.tax_id = amlatr.account_tax_id
        WHERE amlatr.account_tax_id IS NULL
        ON CONFLICT DO NOTHING""",
    )
    # Allow pass check_balance constrain
    openupgrade.logged_query(
        env.cr, """
            UPDATE account_move_line aml
            SET credit = 0.0
            WHERE credit IS NULL
            """,
    )
    openupgrade.logged_query(
        env.cr, """
            UPDATE account_move_line aml
            SET debit = 0.0
            WHERE debit IS NULL
            """,
    )


def compute_balance_for_draft_invoice_lines(env):
    # Compute balance for Draft Invoice Lines
    draft_invoices = env['account.move'].search(
        [('state', 'in', ('draft', 'cancel'))]).with_context(
        check_move_validity=False)
    draft_invoices.line_ids.read()
    draft_invoices.line_ids._onchange_price_subtotal()
    draft_invoices._recompute_dynamic_lines(recompute_all_taxes=True)


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
        'posted', 'paid', av.account_date, av.date_due, av.name,
        av.create_uid, av.create_date, av.write_uid, av.write_date)
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
        currency_id, partner_id, tax_amount, amount, CASE WHEN av.state = 'proforma'
        THEN 'posted' ELSE av.state END, 'not_paid',
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
    # Not draft, cancel, proforma voucher lines
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET exclude_from_invoice_tab = FALSE, sequence = avl.sequence,
        price_unit = avl.price_unit, price_subtotal = avl.price_subtotal,
        old_voucher_line_id = avl.id,
        create_uid = avl.create_uid, create_date = avl.create_date
        FROM account_voucher_line avl
            JOIN account_voucher av ON avl.voucher_id = av.id AND av.state NOT IN ('draft', 'cancel', 'proforma')
            JOIN account_move am ON av.id = am.old_voucher_id
        WHERE am.id = aml.move_id AND avl.company_id = aml.company_id AND avl.account_id = aml.account_id
            AND avl.name = aml.name
            AND avl.quantity = aml.quantity
            AND ((avl.product_id IS NULL AND aml.product_id IS NULL) OR avl.product_id = aml.product_id)
            AND ((avl.account_analytic_id IS NULL AND aml.analytic_account_id IS NULL)
                OR avl.account_analytic_id = aml.analytic_account_id)
        RETURNING aml.id""",
    )
    aml_ids = tuple(x[0] for x in env.cr.fetchall())
    if aml_ids:
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_move_line aml
            SET exclude_from_invoice_tab = TRUE
            FROM account_move_line aml2
            WHERE aml.move_id = aml2.move_id
                AND aml2.old_voucher_line_id IS NOT NULL
                AND aml.old_voucher_line_id IS NULL""",
        )
    # Draft, cancel & proforma voucher lines
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line (company_id, journal_id, account_id,
        exclude_from_invoice_tab, sequence, name, quantity, price_unit, price_subtotal,
        product_id, analytic_account_id, move_id, old_voucher_line_id,
        date, create_uid, create_date, write_uid, write_date)
        SELECT avl.company_id, am.journal_id, avl.account_id, FALSE, avl.sequence, avl.name,
        avl.quantity, avl.price_unit, avl.price_subtotal, avl.product_id,
        avl.account_analytic_id, COALESCE(av.move_id, am.id), avl.id,
        COALESCE(am.date, avl.create_date), avl.create_uid, avl.create_date, avl.write_uid, avl.write_date
        FROM account_voucher_line avl
        JOIN account_voucher av ON avl.voucher_id = av.id AND av.state in ('draft', 'cancel', 'proforma')
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
        ON CONFLICT DO NOTHING""",
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_line_account_tax_rel (
        account_move_line_id, account_tax_id)
        SELECT aml.id, atavlr.account_tax_id
        FROM account_tax_account_voucher_line_rel atavlr
        JOIN account_move_line aml
        ON aml.old_voucher_line_id = atavlr.account_voucher_line_id
        ON CONFLICT DO NOTHING""",
    )


@openupgrade.progress()
def _move_model_in_data(env, id_map, old_model, new_model):
    renames = [
        ('mail_message', 'model', 'res_id'),
        ('mail_followers', 'res_model', 'res_id'),
        ('ir_attachment', 'res_model', 'res_id'),
        ('mail_activity', 'res_model', 'res_id'),
        ('ir_model_data', 'model', 'res_id'),
    ]
    old_id, new_id = id_map
    for rename in renames:
        query = """
            UPDATE {table}
            SET {field1} = %(new_value1)s, {field2} = %(new_value2)s
            WHERE {field1} = %(old_value1)s AND {field2} = %(old_value2)s"""
        if rename[0] == 'mail_followers':
            query += """ AND partner_id NOT IN (
                SELECT partner_id FROM mail_followers
                WHERE res_model = 'account.move' AND res_id = %(new_value2)s
            )"""
        env.cr.execute(sql.SQL(query).format(
            table=sql.Identifier(rename[0]),
            field1=sql.Identifier(rename[1]),
            field2=sql.Identifier(rename[2])
        ), {
            "old_value1": old_model,
            "new_value1": new_model,
            "old_value2": old_id,
            "new_value2": new_id,
        })


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
    taxes_with_children = env['account.tax'].with_context(active_test=False).search(
        [('children_tax_ids', '!=', False)])
    # taxes_children = taxes_with_children.mapped('children_tax_ids')
    complete_taxes = env['account.tax.repartition.line'].search(
        [('invoice_tax_id', '!=', False)]).mapped('invoice_tax_id') | env[
        'account.tax.repartition.line'].search(
        [('refund_tax_id', '!=', False)]).mapped('refund_tax_id')
    tax_ids = (all_taxes - taxes_with_children - complete_taxes).ids
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
    taxes_with_children = env['account.tax.template'].with_context(
        active_test=False).search([('children_tax_ids', '!=', False)])
    # taxes_children = taxes_with_children('children_tax_ids')
    complete_taxes = env['account.tax.repartition.line.template'].search(
        [('invoice_tax_id', '!=', False)]).mapped('invoice_tax_id') | env[
        'account.tax.repartition.line.template'].search(
        [('refund_tax_id', '!=', False)]).mapped('refund_tax_id')
    tax_ids = (all_taxes - taxes_with_children - complete_taxes).ids
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
             atat.account_tax_id = atrl.refund_tax_id)
        ON CONFLICT DO NOTHING"""
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_tax_repartition_financial_tags (
            account_tax_repartition_line_template_id, account_account_tag_id)
        SELECT atrlt.id, aatattr.account_account_tag_id
        FROM account_account_tag_account_tax_template_rel aatattr
        JOIN account_tax_repartition_line_template atrlt ON
            (aatattr.account_tax_template_id = atrlt.invoice_tax_id OR
             aatattr.account_tax_template_id = atrlt.refund_tax_id)
        ON CONFLICT DO NOTHING"""
    )


def assign_tax_repartition_line_to_move_lines(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET tax_repartition_line_id = atrl.id
        FROM account_move_line aml2
        JOIN account_move am ON aml2.move_id = am.id
        JOIN account_invoice_tax ait ON aml2.old_invoice_tax_id = ait.id
        JOIN account_tax at ON ait.tax_id = at.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.invoice_tax_id = at.id AND atrl.repartition_type = 'tax')
        WHERE aml.id = aml2.id
            AND am.type in ('out_invoice', 'in_invoice')"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET tax_repartition_line_id = atrl.id
        FROM account_move_line aml2
        JOIN account_move am ON aml2.move_id = am.id
        JOIN account_invoice_tax ait ON aml2.old_invoice_tax_id = ait.id
        JOIN account_tax at ON ait.tax_id = at.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.refund_tax_id = at.id AND atrl.repartition_type = 'tax')
        WHERE aml.id = aml2.id
            AND am.type in ('out_refund', 'in_refund')"""
    )


def assign_account_tags_to_move_lines(env):
    # move lines with tax repartition lines
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_tax_repartition_line atrl ON aml.tax_repartition_line_id = atrl.id
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        ON CONFLICT DO NOTHING"""
    )
    # move lines with taxes
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        JOIN account_move_line_account_tax_rel amlatr ON amlatr.account_move_line_id = aml.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.invoice_tax_id = amlatr.account_tax_id AND atrl.repartition_type = 'base')
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        WHERE aml.old_invoice_line_id IS NOT NULL AND am.type in ('out_invoice', 'in_invoice')
        ON CONFLICT DO NOTHING"""
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        JOIN account_move_line_account_tax_rel amlatr ON amlatr.account_move_line_id = aml.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.refund_tax_id = amlatr.account_tax_id AND atrl.repartition_type = 'base')
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        WHERE aml.old_invoice_line_id IS NOT NULL AND am.type in ('out_refund', 'in_refund')
        ON CONFLICT DO NOTHING"""
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
    assign_tax_repartition_line_to_move_lines(env)
    assign_account_tags_to_move_lines(env)
    compute_balance_for_draft_invoice_lines(env)
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
            "account.account_invoice_line_comp_rule",
            "account.invoice_comp_rule",
            "account.voucher_comp_rule",
            "account.voucher_line_comp_rule",
            "account.account_payment_term_net",
            "account.reconciliation_model_default_rule",
        ]
    )
