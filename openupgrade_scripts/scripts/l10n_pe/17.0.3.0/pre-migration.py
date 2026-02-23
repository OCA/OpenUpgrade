# Copyright 2026 Tecnativa - David Bañón Gil
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_xml_id_account_fiscal_position(env):
    """In 17.0 account.fiscal.position.tax and account.fiscal.position.account don't
    have xml_id, so let's remove it for companies with this CoA.
    """
    for company in (
        env["res.company"]
        .with_context(active_test=False)
        .search([("chart_template", "=", "pe")])
    ):
        openupgrade.logged_query(
            env.cr,
            f"""
            DELETE FROM ir_model_data
            WHERE module='l10n_pe'
            AND model IN (
                'account.fiscal.position.tax', 'account.fiscal.position.account'
            ) AND name LIKE '{company.id}_%'
            """,
        )
    # Also remove xmlids for fiscal position templates
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE module='l10n_pe'
        AND model IN (
            'account.fiscal.position.template', 'account.fiscal.position.tax.template'
        )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _remove_xml_id_account_fiscal_position(env)
