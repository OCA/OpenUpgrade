# Copyright 2026 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _assign_default_rounding_account(env):
    fr_company_ids = (
        env["res.company"]
        .search([])
        .filtered(lambda c: c.country_code in c._get_france_country_codes())
    )
    for company in fr_company_ids:
        company.l10n_fr_rounding_difference_loss_account_id = env.ref(
            f"account.{company.id}_pcg_4768", False
        )
        company.l10n_fr_rounding_difference_profit_account_id = env.ref(
            f"account.{company.id}_pcg_4778", False
        )


@openupgrade.migrate()
def migrate(env, version):
    _assign_default_rounding_account(env)
    l10n_fr_xmlids = [
        "tax_group_tva_0",
        "tax_group_tva_10",
        "tax_group_tva_20",
        "tax_group_tva_21",
        "tax_group_tva_55",
        "tax_group_tva_85",
    ]
    openupgrade.delete_records_safely_by_xml_id(
        env, [f"l10n_fr.{ref}" for ref in l10n_fr_xmlids]
    )
