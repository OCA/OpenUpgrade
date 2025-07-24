# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "l10n_dk", "17.0.1.3/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "l10n_dk",
        [
            "account_tag_Goodwill_licenses_etc",
            "account_tag_Payroll_related_liabilities",
            "account_tag_administration_costs",
            "account_tag_bank_loans",
            "account_tag_cars_equipment_costs",
            "account_tag_credit_institutions",
            "account_tag_direct_costs",
            "account_tag_equity_corporations",
            "account_tag_equity_individual_enterprises",
            "account_tag_extraordinary_expenses",
            "account_tag_extraordinary_income",
            "account_tag_financial_expenses",
            "account_tag_financial_income",
            "account_tag_inventories",
            "account_tag_land_buildings",
            "account_tag_liquidity",
            "account_tag_other_current_liabilities",
            "account_tag_other_equipment_tools_inventory",
            "account_tag_other_receivables",
            "account_tag_payable",
            "account_tag_prepayments",
            "account_tag_prepayments_from_customers",
            "account_tag_receivable",
            "account_tag_revenue",
            "account_tag_rooms_costs",
            "account_tag_sales_promotions_costs",
            "account_tag_staff_costs",
            "account_tag_vat_taxes",
            "account_tag_work_in_progress",
        ],
        ["name"],
    )
