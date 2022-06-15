from openupgradelib import openupgrade


def _convert_field_to_html(env):
    openupgrade.convert_field_to_html(
        env.cr, "res_company", "invoice_terms", "invoice_terms"
    )
    openupgrade.convert_field_to_html(env.cr, "account_fiscal_position", "note", "note")
    openupgrade.convert_field_to_html(env.cr, "account_move", "narration", "narration")
    openupgrade.convert_field_to_html(env.cr, "account_payment_term", "note", "note")


def _fast_fill_account_move_always_tax_exigible(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS always_tax_exigible BOOLEAN""",
    )
    # 1. Set always_tax_exigible = False if record.is_invoice(True) is True
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET always_tax_exigible = false
        WHERE move_type IN (
            'out_invoice',
            'out_refund',
            'in_refund',
            'in_invoice',
            'out_receipt',
            'in_receipt')
        """,
    )
    # 2. Set always_tax_exigible = False
    #    if record._collect_tax_cash_basis_values() is True
    # 2.1 Set always_tax_exigible = True if invoice is multiple involved currencies
    #     else False
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET always_tax_exigible =
            CASE
                WHEN (SELECT COUNT(aml.currency_id)
                     FROM account_move_line aml
                     WHERE aml.move_id = am.id) > 1
                THEN true
                ELSE false
            END
        WHERE am.always_tax_exigible IS NULL""",
    )
    # 2. Set always_tax_exigible = False
    #    if record._collect_tax_cash_basis_values() is True
    # 2.2 Set always_tax_exigible = False
    #     if any(line.account_internal_type in ('receivable', 'payable')
    #     else True
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET always_tax_exigible =
            CASE
                WHEN (
                    SELECT COUNT(*)
                    FROM account_move_line aml
                    JOIN account_account aa ON aa.id = aml.account_id
                    JOIN account_account_type aat ON aat.id = aa.user_type_id
                    WHERE aml.move_id = am.id
                    AND aat.type IN ('receivable', 'payable')) > 0
                THEN false
                ELSE true
            END
        WHERE am.always_tax_exigible IS NULL""",
    )
    # 2. Set always_tax_exigible = False
    #    if record._collect_tax_cash_basis_values() is True
    # 2.3 Set always_tax_exigible = False
    #     if any(line.tax_line_id.tax_exigibility == 'on_payment')
    #     else True
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET always_tax_exigible =
            CASE
                WHEN (
                    SELECT COUNT(*)
                    FROM account_move_line aml
                    JOIN account_tax tax ON tax.tax_exigibility = 'on_payment'
                        AND aml.tax_line_id = tax.id
                    WHERE aml.move_id = am.id) > 0
                THEN false
                ELSE true
            END
        WHERE am.always_tax_exigible IS NULL""",
    )
    # 2. Set always_tax_exigible = False
    #    if record._collect_tax_cash_basis_values() is True
    # 2.4 Set always_tax_exigible = False
    #     if any(line.tax_ids.tax_exigibility == 'on_payment')
    #     else True
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET always_tax_exigible =
            CASE WHEN (
                SELECT COUNT(aml_tax_rel.account_tax_id)
                FROM account_move_line_account_tax_rel aml_tax_rel
                JOIN account_move_line aml ON aml.id = aml_tax_rel.account_move_line_id
                    AND aml.move_id = am.id
                JOIN account_tax tax ON tax.tax_exigibility = 'on_payment'
                    AND tax.id = aml_tax_rel.account_tax_id) > 0
            THEN false
            ELSE true
            END
        WHERE am.always_tax_exigible IS NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET always_tax_exigible = false
        WHERE always_tax_exigible IS NULL""",
    )


def _fast_fill_account_move_amount_total_in_currency_signed(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS amount_total_in_currency_signed NUMERIC""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET amount_total_in_currency_signed =
            CASE
                WHEN move_type = 'entry'
                THEN ABS(amount_total)
                WHEN move_type IN ('in_invoice', 'out_refund', 'in_receipt')
                THEN -amount_total
                ELSE amount_total
                END""",
    )


def _fast_fill_account_move_line_tax_tag_invert(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move_line
        ADD COLUMN IF NOT EXISTS tax_tag_invert BOOLEAN""",
    )
    # 1. Invoices imported from other softwares might only have kept the tags,
    # not the taxes
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert = CASE
            WHEN (SELECT COUNT(account_account_tag_id)
                FROM account_account_tag_account_move_line_rel
                WHERE aml.id = account_move_line_id) > 0
                    AND am.move_type IN ('out_invoice', 'in_refund', 'out_receipt')
            THEN true
            ELSE false
            END
        FROM account_move am
        WHERE tax_repartition_line_id IS NULL
            AND (
                SELECT COUNT(account_tax_id)
                FROM account_move_line_account_tax_rel
                WHERE aml.id = account_move_line_id) = 0
            AND am.id = aml.move_id
        """,
    )
    # 2. For invoices with taxes
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert = CASE
            WHEN am.move_type IN ('out_invoice', 'in_refund', 'out_receipt')
            THEN true
            ELSE false
            END
        FROM account_move am
        WHERE am.id = aml.move_id AND am.move_type != 'entry'
            AND aml.tax_tag_invert IS NULL""",
    )
    # 3. For misc operations,
    # cash basis entries and write-offs from the bank reconciliation widget
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert =
            CASE
                WHEN (SELECT COALESCE(refund_tax.type_tax_use, invoice_tax.type_tax_use)
                    FROM account_tax_repartition_line atpl
                    JOIN account_tax refund_tax ON refund_tax.id = refund_tax_id
                    JOIN account_tax invoice_tax ON invoice_tax.id = invoice_tax_id
                    WHERE atpl.id = aml.tax_repartition_line_id) = 'purchase'
                THEN (SELECT refund_tax_id
                    FROM account_tax_repartition_line
                    WHERE id = aml.tax_repartition_line_id) IS NOT NULL
                WHEN (SELECT COALESCE(refund_tax.type_tax_use, invoice_tax.type_tax_use)
                    FROM account_tax_repartition_line atpl
                    JOIN account_tax refund_tax ON refund_tax.id = refund_tax_id
                    JOIN account_tax invoice_tax ON invoice_tax.id = invoice_tax_id
                    WHERE atpl.id = aml.tax_repartition_line_id) = 'sale'
                THEN (SELECT refund_tax_id
                    FROM account_tax_repartition_line
                    WHERE id = aml.tax_repartition_line_id) IS NULL
                ELSE false
            END
        FROM account_move am
        WHERE am.id = aml.move_id AND am.move_type = 'entry'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert =
            CASE
                WHEN (SELECT at.type_tax_use
                    FROM account_move_line_account_tax_rel
                    JOIN account_tax at ON at.id = account_tax_id
                    WHERE aml.id = account_move_line_id
                    LIMIT 1) = 'purchase'
                THEN aml.credit > 0
                WHEN (SELECT at.type_tax_use
                    FROM account_move_line_account_tax_rel
                    JOIN account_tax at ON at.id = account_tax_id
                    WHERE aml.id = account_move_line_id
                    LIMIT 1) = 'sale'
                THEN aml.debit > 0
            END
        FROM account_move am
        WHERE am.id = aml.move_id AND
        am.move_type = 'entry' AND
        aml.tax_tag_invert IS NULL AND
        (SELECT COUNT(account_tax_id)
            FROM account_move_line_account_tax_rel
            WHERE aml.id = account_move_line_id) > 0""",
    )


def _create_account_payment_method_line(env):
    # Create account_payment_method_line table
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE account_payment_method_line (
            id SERIAL,
            journal_id INTEGER,
            name varchar,
            payment_account_id INTEGER,
            payment_method_id INTEGER NOT NULL,
            sequence INTEGER,
            CONSTRAINT account_payment_method_line_pkey PRIMARY KEY (id)
        )""",
    )
    # Create account payment method lines from account payment methods
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_method_line
        (name, payment_method_id, journal_id)
        SELECT apm.name, apm.id, aj.id
        FROM account_payment_method apm
        JOIN account_journal aj ON aj.type IN ('bank', 'cash')
        WHERE apm.code = 'manual'
        """,
    )


def _fast_fill_account_payment_payment_method_line_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS payment_method_line_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET payment_method_line_id = apml.id
        FROM account_move am
        JOIN account_payment_method_line apml ON apml.journal_id = am.journal_id
        WHERE ap.move_id = am.id
        """,
    )


def _fill_account_tax_country_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax
        ADD COLUMN IF NOT EXISTS country_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax at
        SET country_id = p.country_id
        FROM res_company c
        JOIN res_partner p ON p.id = c.partner_id
        WHERE c.id = at.company_id
        """,
    )


def _fill_res_company_account_journal_payment_credit_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS account_journal_payment_credit_account_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company c
        SET account_journal_payment_credit_account_id = (
        SELECT aj.payment_credit_account_id
        FROM account_journal aj
        WHERE aj.company_id = c.id AND aj.type IN ('bank', 'cash')
            AND aj.payment_credit_account_id IS NOT NULL
        LIMIT 1)
        """,
    )


def _fill_res_company_account_journal_payment_debit_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS account_journal_payment_debit_account_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company c
        SET account_journal_payment_debit_account_id = (
        SELECT aj.payment_debit_account_id
        FROM account_journal aj
        WHERE aj.company_id = c.id AND aj.type IN ('bank', 'cash')
            AND aj.payment_debit_account_id IS NOT NULL
        LIMIT 1)
        """,
    )


def _fast_fill_account_payment_outstanding_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS outstanding_account_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET outstanding_account_id = CASE
            WHEN apml.payment_account_id IS NOT NULL
                THEN apml.payment_account_id
            END
        FROM account_payment_method_line apml
        WHERE ap.payment_method_line_id IS NOT NULL
            AND apml.id = ap.payment_method_line_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET outstanding_account_id = CASE
            WHEN ap.payment_type = 'inbound'
                AND c.account_journal_payment_debit_account_id IS NOT NULL
                THEN c.account_journal_payment_debit_account_id
            WHEN ap.payment_type = 'outbound'
                AND c.account_journal_payment_credit_account_id IS NOT NULL
                THEN c.account_journal_payment_credit_account_id
            ELSE null
            END
        FROM account_move am
        JOIN account_journal aj ON am.journal_id = aj.id
        JOIN res_company c ON c.id = aj.company_id
        WHERE ap.move_id = am.id AND ap.payment_method_line_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "account", ["action_account_resequence"], True
    )
    openupgrade.rename_columns(
        env.cr,
        {
            "account_move": [
                ("tax_cash_basis_move_id", "tax_cash_basis_origin_move_id"),
            ],
        },
    )
    _convert_field_to_html(env)
    _fast_fill_account_move_always_tax_exigible(env)
    _fast_fill_account_move_amount_total_in_currency_signed(env)
    _fast_fill_account_move_line_tax_tag_invert(env)
    _create_account_payment_method_line(env)
    _fast_fill_account_payment_payment_method_line_id(env)
    _fill_res_company_account_journal_payment_credit_account_id(env)
    _fill_res_company_account_journal_payment_debit_account_id(env)
    _fast_fill_account_payment_outstanding_account_id(env)
    _fill_account_tax_country_id(env)
