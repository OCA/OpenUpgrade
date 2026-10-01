# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo import fields


def update_from_coa_generic(env, spec):
    """
    Update some models from the COA according to spec:
    {model_name1: [fieldname1, fieldname2, ...], model_name2: [...], ...}

    TODO: Move this to openupgradelib if needed for more migrations than
    account, stock_account
    """

    for company in env["res.company"].search([]):
        AccountChartTemplate = env["account.chart.template"].with_context(
            default_company_id=company.id,
            allowed_company_ids=company.ids,
            tracking_disable=True,
            delay_account_group_sync=True,
            lang="en_US",
            chart_template_load=True,
        )

        if company.chart_template not in AccountChartTemplate._template_register:
            openupgrade.logger.error(
                "chart template %s unknown (not yet migrated?)",
                company.chart_template,
            )
            continue

        def ref_or_id(ref_or_id, model_name, AccountChartTemplate=AccountChartTemplate):
            if isinstance(ref_or_id, int):
                return env[model_name].browse(ref_or_id)
            return AccountChartTemplate.ref(ref_or_id, False) or env[model_name].browse(
                []
            )

        template_data = AccountChartTemplate._get_chart_template_data(
            company.chart_template
        )

        company_data = {}
        for model_name, field_names in spec.items():
            filtered_records = {}
            for record_id, record_data in template_data[model_name].items():
                record = ref_or_id(record_id, model_name)
                if not record or not any(record_data.get(key) for key in field_names):
                    # record doesn't exist yet in this company's chart;
                    # don't partially-create it here, only backfill existing ones
                    continue
                filtered = {
                    key: value
                    for key, value in record_data.items()
                    if key in field_names and not record[key]
                }
                if filtered:
                    filtered_records[record_id] = filtered
            company_data[model_name] = filtered_records
        AccountChartTemplate._load_data(company_data)


def update_from_coa(env):
    """
    Set fields account.account#{account_stock_expense_id,account_stock_variation_id}
    and res.company#{account_stock_journal_id,account_stock_valuation_id}
    from localization if not set elsewhere and the localization sets it
    """
    update_from_coa_generic(
        env,
        {
            "res.company": ["account_stock_journal_id", "account_stock_valuation_id"],
            "account.account": [
                "account_stock_expense_id",
                "account_stock_variation_id",
            ],
        },
    )


def stock_lot_avg_cost(env):
    """
    Run compute method on stock.lot#avg_cost
    """
    lots = (
        env["stock.lot"]
        .search(
            [
                ("lot_valuated", "=", True),
            ]
        )
        .with_context(to_date=fields.Datetime.now())
    )
    for records in openupgrade.chunked(lots):
        records._compute_avg_cost()


def stock_move_is_fields(env):
    """
    Run compute methods for  stock.move#is_*
    """
    moves = env["stock.move"].search(
        [
            ("state", "=", "done"),
        ]
    )
    for records in openupgrade.chunked(moves):
        records._compute_is_in()
        records._compute_is_out()
        records._compute_is_dropship()


@openupgrade.migrate()
def migrate(env, version):
    update_from_coa(env)
    stock_lot_avg_cost(env)
    stock_move_is_fields(env)
