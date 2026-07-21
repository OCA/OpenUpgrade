# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from openupgradelib import openupgrade

from odoo.orm.commands import Command


def account_reconcile_model(env):
    """
    Apply changes to account.reconcile.model
    """
    env.cr.execute(
        """
        UPDATE account_reconcile_model
        SET trigger='auto_reconcile'
        WHERE auto_reconcile
        """
    )


def account_reconcile_model_partner_mapping(env):
    """
    Model account.reconcile.model.partner.mapping is folded into
    account.reconcile.model.line, so create a new model per partner
    mapping, merge regexes from partner mapping and model if any
    """
    link_column = openupgrade.get_legacy_name("partner_mapping_id")
    env.cr.execute(
        "ALTER TABLE account_reconcile_model "
        f"ADD COLUMN IF NOT EXISTS {link_column} int "
    )
    env.cr.execute(
        """
        SELECT
        model_id,
        array_agg(id),
        array_agg(partner_id),
        array_agg(payment_ref_regex),
        array_agg(narration_regex)
        FROM account_reconcile_model_partner_mapping mapping
        GROUP BY model_id
        """
    )
    AccountReconcileModel = env["account.reconcile.model"]
    ResPartner = env["res.partner"]

    for (
        reconcile_model_id,
        mapping_ids,
        partner_ids,
        payment_ref_regexes,
        narration_regexes,
    ) in env.cr.fetchall():
        reconcile_model = AccountReconcileModel.browse(reconcile_model_id)
        match_regex_lookahead = ""
        if reconcile_model.match_label_param:
            if reconcile_model.match_label == "contains":
                match_regex_lookahead = (
                    f"(?=.*{re.escape(reconcile_model.match_label_param)}.*)"
                )
            elif reconcile_model.match_label == "not_contains":
                match_regex_lookahead = (
                    f"(?!{re.escape(reconcile_model.match_label_param)})"
                )
            elif reconcile_model.match_label == "match_regex":
                match_regex_lookahead = f"(?={reconcile_model.match_label_param})"

        for mapping_id, partner_id, payment_ref_regex, narration_regex in zip(
            mapping_ids,
            partner_ids,
            payment_ref_regexes,
            narration_regexes,
            strict=True,
        ):
            partner = ResPartner.browse(partner_id)
            match_regex = "|".join(
                map(
                    lambda x: f"({x})",
                    filter(None, [payment_ref_regex, narration_regex]),
                )
            )
            new_reconcile_model = reconcile_model.copy(
                {
                    "name": reconcile_model.name + f" ({partner.name})",
                    "match_label": "match_regex",
                    "match_label_param": match_regex_lookahead + match_regex,
                    "line_ids": [
                        Command.create(
                            {
                                "partner_id": partner_id,
                            }
                        ),
                    ],
                }
            )
            env.cr.execute(
                f"""
                UPDATE account_reconcile_model
                SET {link_column} = {mapping_id}
                WHERE id = {new_reconcile_model.id}
                """
            )


def account_account_active(env):
    """
    Set active flag from deprecated
    """
    env.cr.execute("UPDATE account_account SET active = FALSE where deprecated")


def fiscal_position_tax_ids(env):
    """
    Fill account.fiscal.position#tax_ids from previous account.fiscal.position.tax
    table
    """
    env.cr.execute(
        """
        INSERT INTO account_fiscal_position_account_tax_rel
        (account_fiscal_position_id, account_tax_id)
        SELECT DISTINCT position_id, tax_dest_id FROM account_fiscal_position_tax
        WHERE tax_dest_id IS NOT NULL
        """
    )


def account_tax_original_tax_ids(env):
    """
    Fill account.tax#original_tax_ids from previous account.fiscal.position.tax table
    """
    env.cr.execute(
        """
        INSERT INTO account_tax_alternatives
        (dest_tax_id, src_tax_id)
        SELECT DISTINCT tax_dest_id, tax_src_id FROM account_fiscal_position_tax
        WHERE tax_dest_id IS NOT NULL AND tax_src_id IS NOT NULL
        """
    )


def account_full_reconcile_exchange_move_id(env):
    """
    account.full.reconcile#exchange_move_id has been scrapped, clone a partial
    reconciliation and link the exchange move to it
    """
    env.cr.execute(
        """
        SELECT id, exchange_move_id
        FROM account_full_reconcile
        WHERE exchange_move_id IS NOT NULL
        """
    )
    AccountFullReconcile = env["account.full.reconcile"]

    for full_reconcile_id, exchange_move_id in env.cr.fetchall():
        AccountFullReconcile.browse(full_reconcile_id).partial_reconcile_ids[-1:].copy(
            {
                "exchange_move_id": exchange_move_id,
                "full_reconcile_id": full_reconcile_id,
            }
        )


def account_move_line_no_followup(env):
    """
    Set no_followup = True on lines of journals of type 'general'
    """
    env.cr.execute(
        """
        UPDATE account_move_line
        SET no_followup=True
        FROM account_journal
        WHERE
        account_move_line.journal_id=account_journal.id AND
        account_journal.type = 'general'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "account", "19.0.1.4/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        [
            "email_template_edi_credit_note",
            "email_template_edi_invoice",
            "email_template_edi_self_billing_credit_note",
            "mail_template_data_payment_receipt",
        ],
        ["body_html"],
    )
    account_reconcile_model(env)
    account_reconcile_model_partner_mapping(env)
    account_account_active(env)
    fiscal_position_tax_ids(env)
    account_tax_original_tax_ids(env)
    account_full_reconcile_exchange_move_id(env)
    account_move_line_no_followup(env)
