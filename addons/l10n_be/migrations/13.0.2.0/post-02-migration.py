from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)

# Based on file l10n_be/data/account_tax_template_data.xml
# Also based on Mis Builder VAT report
# (Cadre I, II et III -> base, Cardre IV and following -> tax).
base_tag_xmlids = [
    "tax_tag_00",
    "tax_tag_01",
    "tax_tag_02",
    "tax_tag_03",
    "tax_tag_44",
    "tax_tag_45",
    "tax_tag_46L",
    "tax_tag_46T",
    "tax_tag_47",
    "tax_tag_48s44",
    "tax_tag_48s46L",
    "tax_tag_48s46T",
    "tax_tag_49",
    "tax_tag_81",
    "tax_tag_82",  # Also in tax (see line 1816), consider it as base
    "tax_tag_83",
    "tax_tag_84",
    "tax_tag_85",  # Also in tax (see line 1839), consider it as base
    "tax_tag_86",
    "tax_tag_87",
    "tax_tag_88",
]
tax_tag_xmlids = [
    "tax_tag_54",
    "tax_tag_55",
    "tax_tag_56",
    "tax_tag_57",
    "tax_tag_59",
    "tax_tag_61",
    "tax_tag_62",
    "tax_tag_63",
    "tax_tag_64",
]
# See replace_not_deductible_tag function
not_deductible_tag_xmlids = [
    "tax_tag_81_not_deductible",
    "tax_tag_82_not_deductible",
    "tax_tag_83_not_deductible",
    "tax_tag_85_not_deductible",
]


def update_tags_on_move_line(env):
    """Based on new account.tax, this function check that
    account.account.tag on account.move.line are correct.
    """
    account_move_line_ids = (
        env["account.move.line"]
        .with_context(active_test=False)
        .search([])
    )
    for move_line_id in account_move_line_ids:
        move_id = move_line_id.move_id
        repartition_id = move_line_id.tax_repartition_line_id
        tax_line_id = move_line_id.tax_line_id
        tax_ids = move_line_id.tax_ids
        tax_base_amount = move_line_id.tax_base_amount

        # If a repartition line exists then apply tags form this
        # repartition line
        if repartition_id:
            new_tag_ids = repartition_id.tag_ids

        # If tax_lin_id exists, then find the right repartition line and
        # apply tags from this repartition line
        elif tax_line_id:
            repartition_line_ids = env["account.tax.repartition.line"]
            if "invoice" in move_id.type:
                repartition_line_ids = tax_line_id.invoice_repartition_line_ids
            elif "refund" in move_id.type:
                repartition_line_ids = tax_line_id.refund_repartition_line_ids
            tax_repartition_ids = repartition_line_ids.filtered(
                lambda r: r.repartition_type == "tax"
            )
            tax_repartition_id = env["account.tax.repartition.line"]
            if len(tax_repartition_ids) > 1:
                for rep in tax_repartition_ids:
                    if move_line_id.account_id == rep.account_id:
                        tax_repartition_id = rep
            elif tax_repartition_ids:
                tax_repartition_id = tax_repartition_ids
            if not repartition_id:
                _logger.error(
                    "No account.tax.repartition.line found for "
                    "account.move.line(%s).",
                    move_line_id.id
                )
            new_tag_ids = tax_repartition_id.tag_ids

        # If tax_ids exists and the tax_base_amount is 0 or null
        # then it's a base line, so apply base repartition line from
        # taxes.
        elif tax_ids and not tax_base_amount:
            repartition_line_ids = env["account.tax.repartition.line"]
            if "invoice" in move_id.type:
                repartition_line_ids = tax_ids.mapped(
                    "invoice_repartition_line_ids"
                )
            elif "refund" in move_id.type:
                repartition_line_ids = tax_ids.mapped(
                    "refund_repartition_line_ids"
                )
            base_repartition_ids = repartition_line_ids.filtered(
                lambda r: r.repartition_type == "base"
            )
            new_tag_ids = base_repartition_ids.mapped("tag_ids")

        else:
            new_tag_ids = env["account.account.tag"]

        # Write new tags
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM account_account_tag_account_move_line_rel
            WHERE account_move_line_id = %s
            """,
            (move_line_id.id,),
        )
        for new_tag_id in new_tag_ids:
            openupgrade.logged_query(
                env.cr,
                """
                INSERT INTO account_account_tag_account_move_line_rel (
                    account_move_line_id,
                    account_account_tag_id
                )
                VALUES (%s, %s)
                """,
                (move_line_id.id, new_tag_id.id),
            )


def remove_wrong_tag(env):
    """
    Remove tags on account.move.line that are not linked to an
    account.tax.
    """
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel
        WHERE account_move_line_id IN (
            SELECT id FROM account_move_line
            WHERE id NOT IN (
                SELECT DISTINCT account_move_line_id
                FROM account_move_line_account_tax_rel
            )
        )
        """
    )


def unlink_tags_from_move_line(env, tag_xmlids):
    """Unlink tags from account.move.line"""
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel r
        WHERE
            account_account_tag_id IN (
                SELECT res_id FROM ir_model_data
                WHERE
                    model = 'account.account.tag' AND
                    module = 'l10n_be' AND
                    name IN (%s)
            )
        """ % ",".join("'"+xmlid+"'" for xmlid in tag_xmlids),
    )


def disable_troublesome_tags(env):
    """Disable old tags"""
    openupgrade.logged_query(env.cr, """
        UPDATE account_account_tag
        SET active = FALSE
        WHERE
            name NOT LIKE '+%' AND
            name NOT LIKE '-%' AND
            applicability = 'taxes'
    """)


@openupgrade.migrate()
def migrate(env, version):
    remove_wrong_tag(env)
    update_tags_on_move_line(env)
    unlink_tags_from_move_line(
        env, base_tag_xmlids + tax_tag_xmlids + not_deductible_tag_xmlids
    )
    disable_troublesome_tags(env)
