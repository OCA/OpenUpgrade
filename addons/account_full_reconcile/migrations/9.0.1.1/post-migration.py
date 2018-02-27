# -*- coding: utf-8 -*-
# © 2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade
from openerp import models, SUPERUSER_ID
from openerp.tools.float_utils import float_round, float_is_zero


_logger = logging.getLogger(__name__)


def assure_reconcile_ref_integrity(cr):
    """Triggers for reconcile_ref have failed across v8 history, and there
    are inconsistencies of journal items reconciled, but without reconcile
    reference. With this, we assure that all are filled before migrating
    the reconciles."""
    openupgrade.logged_query(
        cr,
        """UPDATE account_move_line aml
        SET reconcile_ref = amr.name
        FROM account_move_reconcile amr
        WHERE reconcile_ref IS NULL
        AND aml.reconcile_id = amr.id;"""
    )
    openupgrade.logged_query(
        cr,
        """UPDATE account_move_line aml
        SET reconcile_ref = amr.name
        FROM account_move_reconcile amr
        WHERE reconcile_ref IS NULL
        AND aml.reconcile_partial_id = amr.id;"""
    )


def migrate_reconcile(cr):
    """Migrate account.move.reconcile to account.partial.reconcile and
    account.full.reconcile.

    TODO: Look into foreign exchange writeoff.
    """
    # avoid doing anything if the table has already something in it
    # (already migrated)
    cr.execute("""SELECT count(id) FROM account_full_reconcile""")
    res = cr.fetchone()[0]
    if res:
        return

    class LineRecord:

        def __init__(self, db_record):
            """Initialize attributes from db record."""
            self.id = db_record[0]
            self.combined_reconcile_id = db_record[1]
            self.reconcile_id = db_record[2]
            self.reconcile_ref = db_record[3]
            self.debit = db_record[4]
            self.credit = db_record[5]
            self.date = db_record[6]
            self.amount_residual = db_record[7]  # Start off with full amount
            self.balance = db_record[7]  # Start off with full amount
            self.line_currency_id = db_record[8]
            self.line_currency_rounding = db_record[9]
            self.company_currency_id = db_record[10]
            self.company_currency_rounding = db_record[11]
            self.amount_currency = db_record[12]
            self.company_id = db_record[13]
            self.amount_residual_currency = self.amount_currency

        def __str__(self):
            return (
                "LineRecord: id=%d, debit=%.2f, credit=%.2f,"
                " amount_residual=%.2f" %
                (self.id, self.debit, self.credit, self.amount_residual)
            )

        def __repr__(self):
            return self.__str__()

    def reconcile_records(cr, debit_record, credit_record, full_reconcile_id):
        """Links a credit and debit line through partial reconciliation.

        The amount to be reconciled is dependent on the remaining amount
        in the debit and credit lines, we have to take the absolute
        amount_residual, as it has a negative sign for creditlines.
        """
        amount = min(
            abs(debit_record.amount_residual),
            abs(credit_record.amount_residual)
        )
        currency_id = False
        rate = 1.0
        amount_currency = 0.0
        if debit_record.line_currency_id:
            currency_id = debit_record.line_currency_id
            if debit_record.line_currency_id == credit_record.line_currency_id:
                amount_currency = min(
                    abs(debit_record.amount_residual_currency),
                    abs(credit_record.amount_residual_currency))
            elif debit_record.amount_currency:
                rate = abs(debit_record.balance / debit_record.amount_currency)
                amount_currency = amount / rate
        elif credit_record.line_currency_id and credit_record.amount_currency:
            currency_id = credit_record.line_currency_id
            rate = abs(credit_record.balance / credit_record.amount_currency)
            amount_currency = amount / rate
        cr.execute(
            """
            INSERT INTO account_partial_reconcile (
                amount,
                amount_currency,
                currency_id,
                credit_move_id,
                debit_move_id,
                full_reconcile_id,
                company_id,
                create_date,
                create_uid,
                write_date,
                write_uid
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s,
                   CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP, %s)
            """,
            params=(
                amount,
                amount_currency,
                currency_id or None,
                credit_record.id,
                debit_record.id,
                full_reconcile_id or None,
                debit_record.company_id or None,
                SUPERUSER_ID,
                SUPERUSER_ID
            )
        )
        debit_record.amount_residual -= amount
        credit_record.amount_residual += amount
        debit_record.amount_residual_currency -= amount_currency
        credit_record.amount_residual_currency += amount_currency

    def create_full_reconcile(cr, name):
        """Creates full reconcile and returns id of new record."""
        cr.execute(
            """
            INSERT INTO account_full_reconcile (
                name,
                create_date,
                create_uid,
                write_date,
                write_uid
            )
            VALUES(%s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP, %s)
            RETURNING id
            """,
            params=(
                name,
                SUPERUSER_ID,
                SUPERUSER_ID,
            )
        )
        return cr.fetchone()[0]

    def update_account_move_line(cr, move_lines, full_reconcile_id):
        """Update move lines."""
        for line in move_lines:
            # Compute reconciled similar to what happens in model, but using
            # data retrieved using SQL:
            reconciled = False
            digits_rounding_precision = line.company_currency_rounding
            if float_is_zero(
                    line.amount_residual,
                    precision_rounding=digits_rounding_precision):
                if line.line_currency_id and line.amount_residual_currency:
                    # if there is an amount in another currency, it must
                    # be zero as well:
                    currency_zero = float_is_zero(
                        line.amount_residual_currency,
                        precision_rounding=line.line_currency_rounding
                    )
                    if currency_zero:
                        reconciled = True
                else:
                    # no currency involved:
                    reconciled = True
            cr.execute(
                """
                UPDATE account_move_line SET
                    amount_residual = %s,
                    amount_residual_currency = %s,
                    reconciled = %s,
                    balance = %s,
                    company_currency_id = %s,
                    full_reconcile_id = %s,
                    write_date = CURRENT_TIMESTAMP,
                    write_uid = %s
                WHERE id = %s
                """,
                params=(
                    float_round(
                        line.amount_residual,
                        precision_rounding=line.company_currency_rounding
                    ),
                    float_round(
                        line.amount_residual_currency,
                        precision_rounding=line.company_currency_rounding
                    ),
                    reconciled,
                    line.balance,
                    line.company_currency_id,
                    full_reconcile_id or None,
                    SUPERUSER_ID,
                    line.id
                )
            )

    def handle_complete_reconciliation(cr, debit_lines, credit_lines):
        """Each time a move line has another reconcile id, we can
        migrate the 8.0 reconciliation in full."""
        if not debit_lines and not credit_lines:
            return
        record = debit_lines and debit_lines[0] or credit_lines[0]
        full_reconcile_id = (
            record.reconcile_id and
            create_full_reconcile(cr, record.reconcile_ref) or
            False
        )
        # 0. Handle situation with only debit or credit lines:
        if not credit_lines:
            update_account_move_line(cr, debit_lines, full_reconcile_id)
            return
        if not debit_lines:
            update_account_move_line(cr, credit_lines, full_reconcile_id)
            return
        # 1. Reconcile equal amounts:
        for debit_record in debit_lines:
            for credit_record in credit_lines:
                if debit_record.amount_residual == \
                        -credit_record.amount_residual and \
                        debit_record.amount_residual > 0:
                    reconcile_records(
                        cr, debit_record, credit_record, full_reconcile_id
                    )
                    break
        # 2. Reconcile unequal amounts:
        current_debit = 0
        current_credit = 0
        last_debit = len(debit_lines) - 1
        last_credit = len(credit_lines) - 1
        while True:
            debit_record = debit_lines[current_debit]
            credit_record = credit_lines[current_credit]
            if (debit_record.amount_residual > 0 and
                    credit_record.amount_residual < 0):
                reconcile_records(
                    cr, debit_record, credit_record, full_reconcile_id
                )
            if current_debit == last_debit and current_credit == last_credit:
                # Nothing more to reconcile
                break
            unexpected_data = True
            if debit_record.amount_residual <= 0 and \
                    current_debit < last_debit:
                current_debit += 1
                unexpected_data = False
            if credit_record.amount_residual >= 0 and \
                    current_credit < last_credit:
                current_credit += 1
                unexpected_data = False
            if unexpected_data:
                # guard against endless loop due to unexpected/wrong data:
                # could be caused by credit line with amount_residual > 0
                # or debit_line with amount_residual < 0.
                if debit_record.amount_residual < 0.0 or \
                        credit_record.amount_residual > 0.0:
                    _logger.error(
                        "Unexpected data prevented reconcile of lines,"
                        " debit_line=%s, credit_line=%s" %
                        (debit_record, credit_record)
                    )
                if current_debit < last_debit:
                    current_debit += 1
                if current_credit < last_credit:
                    current_credit += 1
        # Update amount residual in reconciled records:
        update_account_move_line(cr, debit_lines, full_reconcile_id)
        update_account_move_line(cr, credit_lines, full_reconcile_id)

    # Define generator to loop over potentially huge amount of records in
    # cursor
    def result_iter(cursor, arraysize=1024):
        'An iterator that uses fetchmany to keep memory usage down'
        while True:
            try:
                results = cursor.fetchmany(arraysize)
            except:
                # Assume no more rows to fetch
                cursor.close()
                break
            if not results:
                cursor.close()
                break
            for result in results:
                yield result

    # We need information on possibly two currencies. One for the company
    # one for the alternative currency defined in the line. For clarity
    # we will prefix the first with company_currency_ and the other with
    # line_currency_
    _logger.info("Starting migration of reconciliations.")
    generator_cursor = cr._cnx.cursor()  # Should be in same connection as cr
    generator_cursor.execute(
        """
        SELECT
            aml.id AS id,
            COALESCE(aml.reconcile_id, aml.reconcile_partial_id)
                AS combined_reconcile_id,
            COALESCE(aml.reconcile_id, 0)
                AS reconcile_id,
            aml.reconcile_ref,
            COALESCE(aml.debit, 0.0) AS debit,
            COALESCE(aml.credit, 0.0) AS credit,
            aml.date AS date,
            COALESCE(aml.debit, 0.0) - COALESCE(aml.credit, 0.0)
                AS amount_residual,
            aml.currency_id as line_currency_id,
            line_cur.rounding AS line_currency_rounding,
            com.currency_id as company_currency_id,
            company_cur.rounding AS company_currency_rounding,
            COALESCE(aml.amount_currency, 0.0) AS amount_currency,
            aml.company_id
        FROM account_move_line aml
        JOIN res_company com on aml.company_id = com.id
        LEFT OUTER JOIN res_currency line_cur
            ON aml.currency_id = line_cur.id
        LEFT OUTER JOIN res_currency company_cur
            ON com.currency_id = company_cur.id
        WHERE aml.reconcile_id IS NOT NULL
           OR aml.reconcile_partial_id IS NOT NULL
        ORDER BY
            aml.reconcile_id, aml.reconcile_partial_id, aml.date
        """
    )
    _logger.info("SQL selection for migration of reconciliations complete.")
    current_id = False
    debit_lines = []
    credit_lines = []
    for db_record in result_iter(generator_cursor):
        record = LineRecord(db_record)
        if current_id and current_id != record.combined_reconcile_id:
            handle_complete_reconciliation(cr, debit_lines, credit_lines)
            debit_lines = []  # Reset
            credit_lines = []  # Reset
        current_id = record.combined_reconcile_id
        if record.credit:
            credit_lines.append(record)
        else:
            debit_lines.append(record)
    # Do remaining bunch of records:
    if current_id:
        handle_complete_reconciliation(cr, debit_lines, credit_lines)
    _logger.info("Migration of reconciliations complete.")
    # Now fill amount_residual for move lines that can be reconciled,
    # but have not been reconciled, and therefore were not updated by the
    # migration:
    cr.execute(
        """\
        WITH subquery AS (
            SELECT
                aml.id as id,
                COALESCE(aml.debit, 0.0) - COALESCE(aml.credit, 0.0)
                    AS amount_residual
            FROM account_move_line aml
            JOIN account_account aa on aml.account_id = aa.id
            WHERE aa.reconcile
              AND aml.reconcile_id IS NULL
              AND aml.reconcile_partial_id IS NULL
        )
        UPDATE account_move_line aml
        SET amount_residual = sq.amount_residual,
            amount_residual_currency = aml.amount_currency
        FROM subquery sq
        WHERE aml.id = sq.id
        """
    )
    _logger.info("Updated amount_residual for unreconciled lines.")
    # Now fill many2many relation to link invoices to payments
    cr.execute(
        """\
        WITH payment_lines AS (
            SELECT apr.credit_move_id AS move_line_id, ai.id AS invoice_id
            FROM account_partial_reconcile apr
            JOIN account_move_line aml ON apr.debit_move_id = aml.id
            JOIN account_invoice ai ON aml.move_id = ai.move_id
            GROUP BY apr.credit_move_id, ai.id
            UNION
            SELECT apr.debit_move_id AS move_line_id, ai.id AS invoice_id
            FROM account_partial_reconcile apr
            JOIN account_move_line aml ON apr.credit_move_id = aml.id
            JOIN account_invoice ai ON aml.move_id = ai.move_id
            GROUP BY apr.debit_move_id, ai.id
        ),
        unique_lines AS (
            SELECT move_line_id, invoice_id
            FROM payment_lines
            GROUP BY move_line_id, invoice_id
        )
        INSERT INTO account_invoice_account_move_line_rel
            (account_invoice_id, account_move_line_id)
        SELECT invoice_id, move_line_id
        FROM unique_lines
        """
    )
    _logger.info("Linked invoices to payments.")
    # Now fill fields in account_move and account_move_line that depend
    # on reconciliation:
    # NOTE: matched_percentage can be > 1.0, because it only includes
    # lines in the total amount from receivable and payable accounts,
    # but there are accounts that can be reconciled that do not fit this
    # selection. This is wierd, but the way the computed field is done in
    # standard Odoo.
    cr.execute(
        """\
        WITH move_amounts AS (
            SELECT
                aml.move_id as move_id,
                SUM(ABS(aml.debit - aml.credit)) AS total_amount
            FROM account_move_line aml
            JOIN account_account aa ON aml.account_id = aa.id
            JOIN account_account_type aat ON aa.user_type_id = aat.id
            WHERE aat.type IN ('receivable', 'payable')
            GROUP BY aml.move_id
        ),
        reconciled_amounts AS (
            SELECT
                aml.move_id as move_id,
                SUM(apr.amount) as total_reconciled
            FROM account_move_line aml
            JOIN account_partial_reconcile apr
            ON aml.id = apr.credit_move_id
            OR aml.id = apr.debit_move_id
            GROUP BY aml.move_id
        ), reconciled_percentages AS (
            SELECT
                am.id as move_id,
                CASE
                WHEN COALESCE(ma.total_amount, 0.0) = 0.0 THEN 1.0
                ELSE COALESCE(ra.total_reconciled, 0.0) /
                    COALESCE(ma.total_amount, 0.0)
                END AS matched_percentage
            FROM account_move am
            LEFT OUTER JOIN move_amounts ma ON am.id = ma.move_id
            LEFT OUTER JOIN reconciled_amounts ra ON am.id = ra.move_id
        )
        UPDATE account_move
        SET matched_percentage = ROUND(rp.matched_percentage, 2)
        FROM reconciled_percentages rp
        WHERE account_move.id = rp.move_id
        """
    )
    _logger.info("Updated account_move.matched_percentage.")
    cr.execute(
        """\
        WITH subquery AS (
            SELECT
                aml.id as id,
                CASE
                WHEN aj.type IN ('sale', 'purchase')
                THEN am.matched_percentage * aml.debit
                ELSE aml.debit
                END as debit_cash_basis,
                CASE
                WHEN aj.type IN ('sale', 'purchase')
                THEN am.matched_percentage * aml.credit
                ELSE aml.credit
                END as credit_cash_basis
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_journal aj ON aml.journal_id = aj.id
        )
        UPDATE account_move_line
        SET
            debit_cash_basis = ROUND(sq.debit_cash_basis, 2),
            credit_cash_basis = ROUND(sq.credit_cash_basis, 2),
            balance_cash_basis = ROUND(
                sq.debit_cash_basis - sq.credit_cash_basis, 2)
        FROM subquery sq
        WHERE account_move_line.id = sq.id
        """
    )
    _logger.info("Updated account_move_line *_cash_basis.")


def invoice_recompute(env):
    set_workflow_org = models.BaseModel.step_workflow
    models.BaseModel.step_workflow = lambda *args, **kwargs: None
    to_recompute = env['account.invoice'].search([])
    for field in [
            'residual', 'residual_signed',
            'residual_company_signed', 'reconciled']:
        env.add_todo(env['account.invoice']._fields[field], to_recompute)
    env['account.invoice'].recompute()
    models.BaseModel.step_workflow = set_workflow_org
    _logger.info("Forced recompute of account_invoice fields.")


@openupgrade.migrate(no_version=True, use_env=True)
def migrate(env, version):
    """Thanks to no_version migration will be run on install as well."""
    cr = env.cr
    if not openupgrade.table_exists(cr, 'account_move_reconcile'):
        return  # This avoids errors when this module is installed on fresh DB
    assure_reconcile_ref_integrity(cr)
    migrate_reconcile(cr)
    invoice_recompute(env)
